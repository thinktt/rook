//! Cold absolute-count transport; the native ledger owns all clock arithmetic.
use super::{array, boolean, object, text, Result};
use rook2::{quiescence::Work, work_clock::Ledger};
use serde_json::{json, Value};

fn count(value: &Value, maximum: u64) -> Result<u64> {
    let digits = text(value)?;
    if digits.is_empty() || !digits.bytes().all(|byte| byte.is_ascii_digit()) {
        return Err("work count requires a nonnegative decimal string".into());
    }
    let count: u64 = digits.parse().map_err(|_| "work count exceeds u64")?;
    if count > maximum {
        return Err("work count outside diagnostic domain".into());
    }
    Ok(count)
}

pub(super) fn dispatch(input: &Value) -> Result<Value> {
    object(input, &["events"])?;
    let mut ledger = Ledger::default();
    let mut work = Work::default();
    let mut observations = Vec::new();
    for event in array(&input["events"], 1, 256)? {
        let event = event.as_object().ok_or("expected event object")?;
        if event.len() != 1 {
            return Err("ledger event must contain exactly one event kind".into());
        }
        if let Some(value) = event.get("work") {
            object(value, &["searchUnits", "relationQueries"])?;
            work = Work {
                charged_search_units: count(&value["searchUnits"], 1u64 << 53)?,
                charged_relation_queries: count(&value["relationQueries"], u64::MAX)?,
            };
        } else if let Some(value) = event.get("observe") {
            if !boolean(value)? || observations.len() == 128 {
                return Err("invalid observe event or too many observations".into());
            }
            // The ledger owns an unsigned wrapping word; this transport reports
            // the corresponding signed centisecond interpretation.
            observations.push(ledger.observe(work) as i32);
        } else if let Some(value) = event.get("reset") {
            if !boolean(value)? {
                return Err("reset event requires true".into());
            }
            ledger.reset();
            work = Work::default();
        } else {
            return Err("unknown ledger event".into());
        }
    }
    if observations.is_empty() {
        return Err("ledger sequence requires an observation".into());
    }
    Ok(json!({"observations":observations}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_u64_transport_and_signed_observed_reset_boundary() {
        let maximum = json!({"work":{"searchUnits":"0","relationQueries":"18446744073709551615"}});
        let output = dispatch(
            &json!({"events":[maximum.clone(),{"observe":true},{"reset":true},
            maximum,{"observe":true},{"work":{"searchUnits":"0","relationQueries":"0"}},
            {"reset":true},{"observe":true}]}),
        )
        .unwrap();
        assert_eq!(output, json!({"observations":[2147483647,-2,-2]}));
    }

    #[test]
    fn decimal_and_event_domains_do_not_coerce_invalid_values() {
        for invalid in [
            json!(1),
            json!("-0"),
            json!("1e3"),
            json!(""),
            json!("9007199254740993"),
        ] {
            assert!(dispatch(&json!({"events":[{"work":{"searchUnits":invalid,"relationQueries":"0"}},{"observe":true}]})).is_err());
        }
        assert!(dispatch(&json!({"events":[{"observe":false}]})).is_err());
        assert!(dispatch(&json!({"events":[{"observe":true,"reset":true}]})).is_err());
        assert!(
            dispatch(&json!({"events":[{"work":{"searchUnits":"0","relationQueries":"0"}}]}))
                .is_err()
        );
        assert!(dispatch(&json!({"events":vec![json!({"observe":true});129]})).is_err());
        assert!(dispatch(&json!({"events":[{"work":{"searchUnits":"0","relationQueries":"18446744073709551616"}},{"observe":true}]})).is_err());
        assert!(dispatch(&json!({"events":[{"work":{"searchUnits":"0000","relationQueries":"0000"}},{"observe":true}]})).is_ok());
    }
}

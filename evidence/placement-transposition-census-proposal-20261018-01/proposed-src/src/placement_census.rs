//! Diagnostic-only complete sequential logging. No lookup/cache or result feedback.
use crate::{activity::Activity, position::Position, shelter::Shelter};
use std::cell::RefCell;
use std::fs::{File, OpenOptions};
use std::io::{self, BufWriter, Write};

const SIZE: usize = 124;
const MAX_BYTES: u64 = 20 * 1024 * 1024 * 1024;
const TAIL_RESERVE: u64 = 4096;
thread_local! { static WRITER: RefCell<Option<Writer>> = const { RefCell::new(None) }; }

#[derive(Clone, Copy, Default)]
struct Counts { encounters: [u64; 4], queries: [u64; 4] }
impl Counts {
    fn add(&mut self, fresh: bool, age: u8, queries: u64) -> io::Result<()> {
        let index = usize::from(fresh) * 2 + usize::from(age != 0);
        self.encounters[index] = self.encounters[index].checked_add(1).ok_or_else(overflow)?;
        self.queries[index] = self.queries[index].checked_add(queries).ok_or_else(overflow)?;
        Ok(())
    }
}
fn overflow() -> io::Error { io::Error::other("census integer/byte capacity exceeded") }

struct Writer {
    raw: BufWriter<File>, report: BufWriter<File>,
    limit: u64, raw_bytes: u64, report_bytes: u64,
    epoch: u64, kind: u8, ordinal: u64, current: Counts, total: Counts,
}
impl Writer {
    fn reserve(&self, bytes: u64) -> io::Result<()> {
        let next = self.raw_bytes.checked_add(self.report_bytes).and_then(|n| n.checked_add(bytes)).ok_or_else(overflow)?;
        if next > self.limit { return Err(overflow()); }
        Ok(())
    }
    fn report(&mut self, text: &str) -> io::Result<()> {
        self.reserve(text.len() as u64)?;
        self.report.write_all(text.as_bytes())?;
        self.report_bytes += text.len() as u64;
        Ok(())
    }
    fn raw(&mut self, bytes: &[u8], reserve_tail: bool) -> io::Result<()> {
        self.reserve(bytes.len() as u64 + if reserve_tail { TAIL_RESERVE } else { 0 })?;
        self.raw.write_all(bytes)?;
        self.raw_bytes += bytes.len() as u64;
        Ok(())
    }
    fn close_epoch(&mut self) -> io::Result<()> {
        if self.epoch != 0 {
            self.report(&format!("{{\"type\":\"epoch\",\"id\":{},\"kind\":{},\"encounters\":{:?},\"queries\":{:?}}}\n", self.epoch,self.kind,self.current.encounters,self.current.queries))?;
        }
        Ok(())
    }
    fn epoch(&mut self, kind: u8, position: &Position) -> io::Result<()> {
        assert!(kind == 1 || kind == 2);
        self.close_epoch()?;
        self.epoch = self.epoch.checked_add(1).ok_or_else(overflow)?;
        self.kind = kind; self.current = Counts::default();
        let mut data = [0u8; SIZE];
        data[0] = kind;
        data[4..12].copy_from_slice(&self.epoch.to_le_bytes());
        data[12..20].copy_from_slice(&self.ordinal.to_le_bytes());
        for (to, piece) in data[20..84].iter_mut().zip(position.board) { *to = piece.0; }
        data[116..120].copy_from_slice(&position.primary.to_le_bytes());
        data[120..124].copy_from_slice(&position.secondary.to_le_bytes());
        self.raw(&data, true)
    }
    fn encounter(&mut self, position: &Position, activity: &Activity, shelter: &Shelter, fresh: bool, age: u8) -> io::Result<()> {
        assert!(self.epoch != 0, "census encounter outside an evaluator epoch");
        self.ordinal = self.ordinal.checked_add(1).ok_or_else(overflow)?;
        // Private totals are maintained directly from the actual producer, not parsed records.
        self.current.add(fresh,age,activity.relation_queries)?;
        self.total.add(fresh,age,activity.relation_queries)?;
        let mut data = [0u8; SIZE];
        data[0]=3; data[1]=u8::from(fresh); data[2]=age;
        data[4..12].copy_from_slice(&self.epoch.to_le_bytes());
        data[12..20].copy_from_slice(&self.ordinal.to_le_bytes());
        for (to,piece) in data[20..84].iter_mut().zip(position.board) { *to=piece.0; }
        for (index,value) in activity.pieces.into_iter().chain(activity.pressure).chain(shelter.terms).enumerate() {
            data[84+4*index..88+4*index].copy_from_slice(&value.to_le_bytes());
        }
        data[108..116].copy_from_slice(&activity.relation_queries.to_le_bytes());
        data[116..120].copy_from_slice(&position.primary.to_le_bytes());
        data[120..124].copy_from_slice(&position.secondary.to_le_bytes());
        self.raw(&data,true)
    }
    fn finish(mut self) -> io::Result<()> {
        self.close_epoch()?;
        let mut data=[0u8;SIZE]; data[0]=4;
        data[4..12].copy_from_slice(&self.epoch.to_le_bytes());
        data[12..20].copy_from_slice(&self.ordinal.to_le_bytes());
        let queries=self.total.queries.iter().try_fold(0u64,|n,&q| n.checked_add(q).ok_or_else(overflow))?;
        data[108..116].copy_from_slice(&queries.to_le_bytes());
        self.raw(&data,false)?;
        self.report(&format!("{{\"type\":\"end\",\"epochs\":{},\"ordinal\":{},\"raw_bytes\":{},\"encounters\":{:?},\"queries\":{:?}}}\n",self.epoch,self.ordinal,self.raw_bytes,self.total.encounters,self.total.queries))?;
        self.raw.flush()?; self.report.flush()?;
        self.raw.get_ref().sync_all()?; self.report.get_ref().sync_all()?;
        Ok(())
    }
}

pub fn initialize() -> io::Result<()> {
    let path=std::env::var_os("ROOK2_CENSUS_RAW").ok_or_else(||io::Error::other("missing census raw path"))?;
    let report=std::env::var_os("ROOK2_CENSUS_REPORT").ok_or_else(||io::Error::other("missing census report path"))?;
    let limit: u64=std::env::var("ROOK2_CENSUS_MAX_BYTES").map_err(io::Error::other)?.parse().map_err(io::Error::other)?;
    if !(24+SIZE as u64+TAIL_RESERVE..=MAX_BYTES).contains(&limit) { return Err(overflow()); }
    let raw=OpenOptions::new().write(true).create_new(true).open(path)?;
    let report=OpenOptions::new().write(true).create_new(true).open(report)?;
    let mut writer=Writer { raw:BufWriter::with_capacity(1024*1024,raw),report:BufWriter::new(report),limit,raw_bytes:0,report_bytes:0,epoch:0,kind:0,ordinal:0,current:Counts::default(),total:Counts::default() };
    let mut header=[0u8;24]; header[..8].copy_from_slice(b"R2PLC001");
    header[8..12].copy_from_slice(&1u32.to_le_bytes()); header[12..16].copy_from_slice(&(SIZE as u32).to_le_bytes()); header[16..24].copy_from_slice(&limit.to_le_bytes());
    writer.raw(&header,true)?;
    writer.report(&format!("{{\"type\":\"header\",\"schema\":\"rook2-placement-census-v1\",\"pid\":{},\"byte_limit\":{}}}\n",std::process::id(),limit))?;
    WRITER.with(|state| { assert!(state.borrow().is_none(),"census already initialized"); *state.borrow_mut()=Some(writer); });
    Ok(())
}
pub(crate) fn epoch(kind: u8, position: &Position) {
    WRITER.with(|state| state.borrow_mut().as_mut().expect("census not initialized").epoch(kind,position).expect("census epoch failed"));
}
pub(crate) fn encounter(position: &Position, activity: &Activity, shelter: &Shelter, fresh: bool, age: u8) {
    WRITER.with(|state| state.borrow_mut().as_mut().expect("census not initialized").encounter(position,activity,shelter,fresh,age).expect("census write failed"));
}
pub fn finish() -> io::Result<()> {
    WRITER.with(|state| state.borrow_mut().take().ok_or_else(||io::Error::other("census not initialized"))?.finish())
}

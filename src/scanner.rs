use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};
use walkdir::WalkDir;
use std::ffi::OsStr;
use walkdir::DirEntry;

#[derive(Debug, Clone)]
pub struct FileEntry {
    pub path: String,
    pub name: String,
    pub extension: String,
    pub modified: u64
}

fn checkfile(e: &DirEntry) -> bool {
    e.file_type().is_file()
}

fn convstring(s: &OsStr) -> String {
    s.to_string_lossy().to_string()
}

pub fn scan_dir(root: &Path, include_hidden: bool) -> Vec<FileEntry> {
    let mut results = Vec::new();

    for entry in WalkDir::new(root)
    .follow_links(false)
    .into_iter()
    .filter_map(Result::ok)
    .filter(checkfile)
    {
        let path = entry.path();

        if !include_hidden && is_hidden(path) {
            continue;
        }

        let name = path
        .file_name()
        .map(convstring)
        .unwrap_or_default();

        let extension = path
        .extension()
        .map(convstring)
        .unwrap_or_default();
        
        let modified = std::fs::metadata(path)
        .and_then(|m| m.modified())
        .unwrap_or(SystemTime::UNIX_EPOCH)
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

        results.push(FileEntry{
            path: path.to_string_lossy().to_string(),
            name,
            extension,
            modified
        });
    }
    results
}

fn is_hidden(path: &Path) -> bool {
    path.components().any(|c| {
        c.as_os_str()
        .to_string_lossy()
        .starts_with('.')
    })
}


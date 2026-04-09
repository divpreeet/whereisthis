mod cli;
mod scanner;

use std::path::PathBuf;


fn main() {
    let args = cli::parse_args();
    let root = match args.dir {
        Some(dir) => PathBuf::from(dir),
        None => std::env::current_dir().expect("failed to get current directory")
    };

    let files = scanner::scan_dir(&root, args.hidden);

    println!("scanned {} files in {}", files.len(), root.display());

    for f in files {
        println!("{}", f.path);
    }
}

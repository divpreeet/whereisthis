use clap::Parser;

#[derive(Parser, Debug)]
#[command(name="whereisthis", version, about="human based local file search")]

// arguemnets for cli 
pub struct Args {
    pub query: String,

    // dir with double dash
    #[arg(long)]
    pub dir: Option<String>,

    //file extension
    #[arg(long = "type")]
    pub filetype: Option<String>,

    // max number of results to show
    // note - default_value_t is used for post parsed values like integers, and defualt_valuse is used for strings, pre parsed data
    #[arg(long , default_value_t = 10)]
    pub limit: usize,

    #[arg(long, default_value_t = false)]
    pub hidden: bool
}

pub fn parse_args() -> Args {
    Args::parse()
}
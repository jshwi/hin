use std::env;

use clap::Parser;
use color_eyre::Result;
use hin::{
    commands::{clone, list},
    parser::{Args, Command},
    DOTFILES,
};

fn main() -> Result<()> {
    color_eyre::install()?;
    let name: String = env::var("CARGO_PKG_NAME")?;
    if env::var(DOTFILES).is_err() {
        env::set_var(
            DOTFILES,
            directories::BaseDirs::new().unwrap().data_dir().join(name),
        )
    }
    let args = Args::parse();
    match args.command {
        Command::Add { file } => println!("added {}", file),
        Command::Clone { url } => clone(&url).unwrap(),
        Command::Commit { file } => println!("committed {}", file),
        Command::Install {} => println!("installing"),
        Command::Link { link, target } => {
            println!("linked {} to {}", link, target)
        }
        Command::List {} => list().unwrap(),
        Command::Push {} => println!("pushed"),
        Command::Remove { file } => println!("removed {}", file),
        Command::Status {} => println!("showed status"),
        Command::Undo {} => println!("undone"),
        Command::Uninstall {} => println!("uninstalled"),
    }
    Ok(())
}

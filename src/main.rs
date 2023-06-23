use std::env;

use clap::Parser;
use color_eyre::Result;
use hin::{
    cmd,
    parser::{Args, Command},
    DOTFILES,
};


fn set_repo_path() -> Result<()> {
    let name: String = env::var("CARGO_PKG_NAME")?;
    if env::var(DOTFILES).is_err() {
        env::set_var(
            DOTFILES,
            directories::BaseDirs::new().unwrap().data_dir().join(name),
        )
    };
    Ok(())
}


fn main() -> Result<()> {
    color_eyre::install()?;
    set_repo_path()?;
    let args = Args::parse();
    match args.command {
        Command::Add { file } => cmd::add(file).unwrap(),
        Command::Clone { url } => cmd::clone(url).unwrap(),
        Command::Commit { file } => cmd::commit(file).unwrap(),
        Command::Install {} => cmd::install().unwrap(),
        Command::Link { file, target } => cmd::link(file, target).unwrap(),
        Command::List {} => cmd::list().unwrap(),
        Command::Push {} => cmd::push().unwrap(),
        Command::Remove { file } => cmd::remove(file).unwrap(),
        Command::Status {} => cmd::status().unwrap(),
        Command::Undo {} => cmd::undo().unwrap(),
        Command::Uninstall {} => cmd::uninstall().unwrap(),
    }
    Ok(())
}

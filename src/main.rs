use std::env;

use clap::Parser;
use color_eyre::Result;
use hin::{
    cmd,
    parser::{Args, Command},
    DOTFILES,
};
use log::debug;


fn set_repo_path() -> Result<()> {
    let name: String = env::var("CARGO_PKG_NAME")?;
    debug!("CARGO_PKG_NAME={}", name);
    let repo = env::var(DOTFILES);
    let default = directories::BaseDirs::new().unwrap().data_dir().join(name);
    if repo.is_err() {
        debug!("DOTFILES not set, defaulting to {:?}", default);
        env::set_var(DOTFILES, default)
    } else {
        debug!("DOTFILES={}", repo.unwrap());
    };
    Ok(())
}


fn main() -> Result<()> {
    color_eyre::install()?;
    env_logger::init();
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

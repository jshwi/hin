//! Hin
//! Manage your hidden files
#![warn(missing_docs)]

use clap::Parser;
use color_eyre::Result;
use hin::{
    add::add,
    clone::clone,
    commit::commit,
    config::Config,
    git::Git,
    install::install,
    link::link,
    list::list,
    misc::set_repo_path,
    parser::{Args, Command},
    push::push,
    remove::remove,
    status::status,
    undo::undo,
    uninstall::uninstall,
};

fn main() -> Result<()> {
    color_eyre::install()?;
    env_logger::init();
    let dotfiles = set_repo_path()?;
    let config = Config::new(&dotfiles)?;
    let git = Git::new(&dotfiles)?;
    if !git.dir.is_dir() {
        git.create_initial_commit()?;
    }
    let args = Args::parse();
    match args.command {
        Command::Add { file } => add(file, config, git)?,
        Command::Clone { url } => clone(url)?,
        Command::Commit { file } => commit(file)?,
        Command::Install {} => install(config)?,
        Command::Link { file, target } => link(file, target, config)?,
        Command::List {} => list(config)?,
        Command::Push {} => push()?,
        Command::Remove { file } => remove(file)?,
        Command::Status {} => status()?,
        Command::Undo {} => undo()?,
        Command::Uninstall {} => uninstall(config)?,
    }
    Ok(())
}

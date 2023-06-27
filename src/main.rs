use std::env;

use clap::Parser;
use color_eyre::Result;
use hin::{
    add::add,
    clone::clone,
    commit::commit,
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
    DOTFILES,
};

fn main() -> Result<()> {
    color_eyre::install()?;
    env_logger::init();
    set_repo_path()?;
    git2::Repository::init(env::var(DOTFILES)?)?;
    let args = Args::parse();
    match args.command {
        Command::Add { file } => add(file)?,
        Command::Clone { url } => clone(url)?,
        Command::Commit { file } => commit(file)?,
        Command::Install {} => install()?,
        Command::Link { file, target } => link(file, target)?,
        Command::List {} => list()?,
        Command::Push {} => push()?,
        Command::Remove { file } => remove(file)?,
        Command::Status {} => status()?,
        Command::Undo {} => undo()?,
        Command::Uninstall {} => uninstall()?,
    }
    Ok(())
}

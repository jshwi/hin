use clap::Parser;
use color_eyre::Result;
use hin::{
    add::add,
    clone::clone,
    commit::commit,
    install::install,
    link::link,
    list::list,
    misc::{create_initial_commit, set_repo_path, touch},
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
    let repository = git2::Repository::init(&dotfiles)?;
    touch(&dotfiles.join("dotfiles.ini"))?;
    create_initial_commit(&repository)?;
    let args = Args::parse();
    match args.command {
        Command::Add { file } => add(file, repository)?,
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

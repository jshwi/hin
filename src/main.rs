use clap::Parser;
use color_eyre::Result;
use hin::{
    add::add,
    clone::clone,
    commit::commit,
    config::Config,
    install::install,
    link::link,
    list::list,
    misc::{create_initial_commit, set_repo_path},
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
    let repository = git2::Repository::init(&dotfiles)?;
    create_initial_commit(&repository, &config.path)?;
    let args = Args::parse();
    match args.command {
        Command::Add { file } => add(file, config, repository)?,
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

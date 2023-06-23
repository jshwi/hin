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
};

fn main() -> Result<()> {
    color_eyre::install()?;
    env_logger::init();
    set_repo_path()?;
    let args = Args::parse();
    match args.command {
        Command::Add { file } => add(file).unwrap(),
        Command::Clone { url } => clone(url).unwrap(),
        Command::Commit { file } => commit(file).unwrap(),
        Command::Install {} => install().unwrap(),
        Command::Link { file, target } => link(file, target).unwrap(),
        Command::List {} => list().unwrap(),
        Command::Push {} => push().unwrap(),
        Command::Remove { file } => remove(file).unwrap(),
        Command::Status {} => status().unwrap(),
        Command::Undo {} => undo().unwrap(),
        Command::Uninstall {} => uninstall().unwrap(),
    }
    Ok(())
}

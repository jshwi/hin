use clap::Parser;
use color_eyre::Result;
use hin::{
    add::add,
    cmd,
    install::install,
    link::link,
    misc::set_repo_path,
    parser::{Args, Command},
};

fn main() -> Result<()> {
    color_eyre::install()?;
    env_logger::init();
    set_repo_path()?;
    let args = Args::parse();
    match args.command {
        Command::Add { file } => add(file).unwrap(),
        Command::Clone { url } => cmd::clone(url).unwrap(),
        Command::Commit { file } => cmd::commit(file).unwrap(),
        Command::Install {} => install().unwrap(),
        Command::Link { file, target } => link(file, target).unwrap(),
        Command::List {} => cmd::list().unwrap(),
        Command::Push {} => cmd::push().unwrap(),
        Command::Remove { file } => cmd::remove(file).unwrap(),
        Command::Status {} => cmd::status().unwrap(),
        Command::Undo {} => cmd::undo().unwrap(),
        Command::Uninstall {} => cmd::uninstall().unwrap(),
    }
    Ok(())
}

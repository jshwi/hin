use std::env;

use clap::Parser;
use color_eyre::Result;
use hin::{
    commands::{
        add,
        clone,
        commit,
        install,
        link,
        list,
        push,
        remove,
        status,
        undo,
        uninstall,
    },
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
        Command::Add { file } => add(file).unwrap(),
        Command::Clone { url } => clone(url).unwrap(),
        Command::Commit { file } => commit(file).unwrap(),
        Command::Install {} => install().unwrap(),
        Command::Link { symlink, target } => link(symlink, target).unwrap(),
        Command::List {} => list().unwrap(),
        Command::Push {} => push().unwrap(),
        Command::Remove { file } => remove(file).unwrap(),
        Command::Status {} => status().unwrap(),
        Command::Undo {} => undo().unwrap(),
        Command::Uninstall {} => uninstall().unwrap(),
    }
    Ok(())
}

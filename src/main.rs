use std::{borrow::Cow, env, path::Path};

use clap::{Parser, Subcommand};
use color_eyre::Result;
use git2::Repository;
use ini::Ini;

const DOTFILES: &str = "DOTFILES";

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

/// Dotfile manager.
#[derive(Parser, Debug)]
#[clap(version)]
struct Args {
    #[clap(subcommand)]
    command: Command,
}

#[derive(Subcommand, Debug)]
enum Command {
    /// Add new FILE to version control.
    ///
    /// If the file is a symlink not related to the dotfile repo then
    /// the source of the symlink will be added. The original path will
    /// be symlinked to the versioned file.
    ///
    /// If the source file is a child of an already added directory it
    /// will be added as part of the directory. If the source file is a
    /// child of a directory that has not been added it will be
    /// installed individually, with the parents recreated, if they do
    /// not already exist.
    ///
    /// If the source file is a directory then only the directory will
    /// be added, unless there are child files that have already been
    /// added, in which case they will be unlinked and added to version
    /// control under the source.
    ///
    /// Changes will be committed.
    Add { file: String },
    /// Clone a dotfile repository from a URL.
    Clone { url: String },
    /// Commit changes to FILE.
    Commit { file: String },
    /// Install a dotfile repository.
    ///
    /// Repository needs to contain a dotfiles.ini file consisting of
    /// symlink to dotfile key-value pairs. The config will be parsed
    /// and all checked in files symlinked, relative to the home
    /// directory.
    ///
    /// Any files that share a name with a versioned file will be backed
    /// up and timestamped with the time of the installation.
    ///
    /// Any dangling symlinks that exist are removed if they share a
    /// name with a versioned dotfile.
    Install {},
    /// Create a new LINK from TARGET.
    ///
    /// Create a symlink to an existing linked dotfile, reproducible
    /// with a dotfile installation. This is useful for shared configs.
    ///
    /// This will fail if the target is not a dotfile symlink or a child
    /// of a dotfile symlink.
    ///
    /// The target needs to be a link to a checked in file or dir, or a
    /// versioned descendant of a linked dir. Any other files or dirs
    /// cannot be installed, and the state reproduced, on a clean
    /// system.
    ///
    /// Changes will be committed.
    Link { link: String, target: String },
    /// List all versioned dotfiles.
    List {},
    /// Push changes to remote.
    Push {},
    /// Remove FILE from version control.
    ///
    /// All links that point to the file, and any links to those links,
    /// will be removed.
    ///
    /// If the dotfile is not a link to another dotfile then the checked
    /// in file or directory will be moved back to its original location
    /// in its place.
    ///
    /// Changes will be committed.
    Remove { file: String },
    /// Check version status.
    Status {},
    /// Revert previous commit and actions.
    Undo {},
    /// Uninstall a dotfile repository.
    ///
    /// This will remove all symlinks pointing to the dotfile
    /// repository.
    Uninstall {},
}

fn clone(url: &str) -> Result<()> {
    let dotfiles = &env::var("DOTFILES")?;
    let path = Path::new(&dotfiles);
    let repo_name = url
        .split('/')
        .collect::<Vec<&str>>()
        .pop()
        .unwrap()
        .replace(".git", "");
    println!("cloning '{}' into {:?}", repo_name, path);
    match Repository::clone(url, path) {
        Ok(repo) => repo,
        Err(e) => panic!("failed to clone: {}", e),
    };
    println!(
        "{}",
        ansi_term::Color::Green.bold().paint("cloned dotfile repo")
    );
    Ok(())
}


fn list() -> Result<()> {
    let dotfiles = &env::var("DOTFILES")?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    let config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &config {
        for (key, value) in prop.iter() {
            let kind = ansi_term::Color::Green.bold().paint("+");
            println!("{} {:?}:{:?}", kind, key, value);
        }
    }
    Ok(())
}


fn _context(s: &str) -> Result<Option<Cow<'static, str>>, env::VarError> {
    match env::var(s) {
        Ok(value) => Ok(Some(value.into())),
        Err(env::VarError::NotPresent) => Ok(Some("".into())),
        Err(e) => Err(e),
    }
}


trait FileABC {
    fn name(&self) -> String;
    fn env(&self) -> String;
    fn root(&self) -> String;
    fn relpath(&self) -> String {
        self.name().replace(&self.root(), "")
    }
    fn path(&self) -> String {
        format!("{}/{}", self.root(), self.relpath())
    }
}


impl Symlink {
    fn _new(name: String) -> Symlink {
        Symlink {
            name: shellexpand::env_with_context(&name, _context)
                .unwrap()
                .to_string(),
        }
    }
}


struct Symlink {
    name: String,
}


impl FileABC for Symlink {
    fn name(&self) -> String {
        format!(
            "{:?}/{}",
            home::home_dir(),
            shellexpand::env_with_context(&self.name, _context).unwrap()
        )
    }

    fn env(&self) -> String {
        "HOME".to_string()
    }

    fn root(&self) -> String {
        env::var(self.env()).unwrap()
    }
}

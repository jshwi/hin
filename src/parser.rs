use clap::{Parser, Subcommand};

/// Dotfile manager.
#[derive(Parser, Debug)]
#[clap(version)]
pub struct Args {
    #[clap(subcommand)]
    pub command: Command,
}


#[derive(Subcommand, Debug)]
pub enum Command {
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
    /// Create a new FILE from TARGET.
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
    Link { file: String, target: String },
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

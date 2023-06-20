use clap::{Parser, Subcommand};

fn main() {
    let _args = Args::parse();
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
    Add {},
    /// Clone a dotfile repository from a URL.
    Clone {},
    /// Commit changes to FILE.
    Commit {},
    /// Install a dotfile repository.
    Install {},
    /// Create a new LINK from TARGET.
    Link {},
    /// List all versioned dotfiles.
    List {},
    /// Push changes to remote.
    Push {},
    /// Remove FILE from version control.
    Remove {},
    /// Check version status.
    Status {},
    /// Revert previous commit and actions.
    Undo {},
    /// Uninstall a dotfile repository.
    Uninstall {},
}

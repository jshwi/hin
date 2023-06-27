use std::{env, fs, io::ErrorKind, os::unix::fs::symlink, path::Path};

use color_eyre::Result;
use log::debug;

use crate::{
    config::Config,
    files::{FileTrait, Matrix},
    DOTFILES,
};

pub fn install(config: Config) -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("installing dotfiles configured in {}", path.display());
    for (_, prop) in &config.ini {
        for (key, value) in prop.iter() {
            let dotfile = Matrix::new(&key.to_string(), &value.to_string());
            let mut is_a_dotfiles_link = false;
            if dotfile.key.path().is_symlink() {
                let linksrc = &dotfile.key.path().read_link()?;
                debug!(
                    "{} leads to {}",
                    &dotfile.key.path().display(),
                    linksrc.display()
                );
                debug!("value_path={}", &dotfile.value.path().display());
                if &dotfile.value.path() == linksrc {
                    debug!("is a dotfiles link");
                    is_a_dotfiles_link = true;
                }
            }
            if dotfile.key.path().exists() {
                if is_a_dotfiles_link {
                    debug!(
                        "removing {}, an existing dotfile link",
                        &dotfile.key.path().display()
                    );
                    fs::remove_file(&dotfile.key.path())?;
                } else {
                    let new_key_path = Path::new(
                        &dotfile.key.path().parent().unwrap(),
                    )
                    .join(format!(
                        "{}.{}",
                        &dotfile
                            .key
                            .path()
                            .file_name()
                            .unwrap()
                            .to_str()
                            .unwrap(),
                        chrono::Utc::now().timestamp()
                    ));
                    debug!(
                        "renamed {} to {}",
                        &dotfile.key.path().display(),
                        &new_key_path.display()
                    );
                    fs::rename(&dotfile.key.path(), &new_key_path)?;
                    println!(
                        "{} {}",
                        ansi_term::Color::Yellow.bold().paint("backed up"),
                        &dotfile.key.path().display()
                    )
                }
            }
            loop {
                match symlink(&dotfile.value.path(), &dotfile.key.path()) {
                    Ok(_) => {
                        println!(
                            "{} {}",
                            ansi_term::Color::Green.bold().paint("installed"),
                            &dotfile.key.path().display()
                        );
                        break;
                    }
                    Err(error) => match error.kind() {
                        ErrorKind::AlreadyExists => {
                            debug!(
                                "removing {}, a dangling symlink",
                                &dotfile.key.path().display()
                            );
                            fs::remove_file(&dotfile.key.path())?;
                        }
                        ErrorKind::NotFound => {
                            let path = dotfile.key.path();
                            let parent = path.parent().unwrap();
                            debug!(
                                "{} does not exist, creating",
                                parent.display()
                            );
                            fs::create_dir(parent)?
                        }
                        other_error => {
                            panic!("Problem installing file: {}", other_error);
                        }
                    },
                };
            }
        }
    }
    Ok(())
}

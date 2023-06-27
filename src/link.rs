use color_eyre::Result;
use log::debug;

use crate::{
    config::Config,
    files::{FileTrait, Matrix},
    gitignore::unignore,
};

pub fn link(
    symlink: String,
    target: String,
    mut config: Config,
) -> Result<()> {
    let custom = Matrix::new(&symlink, &target);
    let mut add_to_config = false;
    for (_, prop) in &mut config.ini {
        if prop.contains_key(custom.key.repr()) {
            panic!("{} already added", &symlink)
        }
        for (key, value) in prop.iter() {
            let existing = Matrix::new(&key.to_string(), &value.to_string());
            if custom.is_child_of(&existing)
                && custom.realsrc().value.path().exists()
            {
                debug!(
                    "{} starts with {}",
                    symlink,
                    existing.key.path().display()
                );
                debug!(
                    "or {} starts with {}",
                    symlink,
                    existing.value.path().display()
                );
                debug!("and {} exists", custom.key.relpath().display());
                unignore(&custom.key.relpath(), &existing.key.relpath());
            } else if custom.key.relpath() != existing.value.path() {
                debug!(
                    "{} not equal to {}",
                    custom.key.relpath().display(),
                    existing.value.relpath().display()
                );
                continue;
            }
            add_to_config = true;
            debug!(
                "link {} to {}",
                custom.key.path().display(),
                existing.key.path().display()
            );
            // todo
            //   return f"add {custom.key.path.name}"
            println!(
                "add {}",
                custom.key.path().file_name().unwrap().to_str().unwrap()
            );
            debug!("added {} to config", existing.value.path().display());
            break;
        }
    }
    if add_to_config {
        config.add(&custom.key.repr(), &custom.value.repr());
    } else {
        // todo
        //   make this an error
        panic!(
            "link not related to a symlink or parent of a symlink in dotfile \
             repo"
        );
    }
    Ok(())
}

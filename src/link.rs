use std::{env, path::Path};

use color_eyre::Result;
use ini::Ini;
use log::debug;
use relative_path::RelativePath;

use crate::{gitignore::unignore, misc::is_child_of, DOTFILES};

pub fn link(symlink: String, _target: String) -> Result<()> {
    let dotfiles = &env::var(DOTFILES)?;
    let path = Path::new(dotfiles).join("dotfiles.ini");
    debug!("dotfile configuration: {:?}", path);
    let mut config = Ini::load_from_file(path).unwrap();
    for (_, prop) in &mut config {
        // todo
        //   this only evaluates the string provided and not relative
        //   path, absolute path, etc.
        if prop.contains_key(&symlink) {
            // todo
            //   make this an error
            panic!("{} already added", &symlink)
        }
        for (key, value) in prop.iter() {
            let key_path = shellexpand::env(&key)?.to_string();
            let value_path = shellexpand::env(&value)?.to_string();
            let key_path = Path::new(&key_path);
            let value_path = Path::new(&value_path);
            let rel_new_path = RelativePath::new(&symlink);
            let rel_value_path =
                RelativePath::new(value_path.to_str().unwrap());
            let logical_path = rel_value_path.to_logical_path(dotfiles);
            if is_child_of(&symlink, key_path, value_path)
                && logical_path.exists()
            {
                debug!("{} starts with {:?}", symlink, key_path);
                debug!("or {} starts with {:?}", symlink, value_path);
                debug!("and {:?} exists", logical_path);
                unignore(
                    rel_new_path.to_logical_path(dotfiles),
                    rel_value_path.to_logical_path(dotfiles),
                );
            } else if rel_new_path != rel_value_path {
                debug!("{} not equal to {}", rel_new_path, rel_value_path);
                continue;
            }
            // todo
            //   config.add(custom)
            debug!("link {:?} to {:?}", key_path, value_path);
            // todo
            //   return f"add {custom.key.path.name}"
            debug!("added {:?} to config", value_path);
        }
    }
    // todo
    //   make this an error
    panic!(
        "link not related to a symlink or parent of a symlink in dotfile repo"
    );
}

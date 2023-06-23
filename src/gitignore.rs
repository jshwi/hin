use std::path::PathBuf;

use log::debug;

pub fn unignore(path_1: PathBuf, path_2: PathBuf) {
    debug!("unignoring {:?}: {:?}", path_1, path_2)
}

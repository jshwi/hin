FROM python:3.13.0b1-alpine AS playground
ENV USER=hin VENV=/opt/venv PATH=$VENV/bin:$PATH
WORKDIR /home/$USER
COPY ./hin /opt/hin/hin
COPY ./pyproject.toml ./poetry.lock ./README.rst /opt/hin/
COPY <<'EOF' /opt/entrypoint
#!/bin/sh
rm -rf -- ..?* .[!.]* *
xdg-user-dirs-update
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25; do
  mkdir -p ".config/$i" && touch ".config/$i/file.txt"
  mkdir ".test${i}" && touch ".test${i}/file.txt"
done
mkdir .config/nvim && touch .config/nvim/init.lua
mkdir .vim && touch .vim/vimrc
mkdir -p .level1/level2/level3 && touch .level1/level2/level3/file.txt
mkdir -p .level2/level3/level4 && touch .level2/level3/level4/file.txt
mkdir .linkdir && touch .linkdir/linkfile && ln -s .linkdir/linkfile .link
touch .somerc
git config --global user.name "${USER}"
git config --global user.email "${USER}@localhost"
exec "$@"
EOF
RUN <<EOF
chmod 755 /opt/entrypoint
adduser --disabled-password $USER
apk add --no-cache git xdg-user-dirs
python -m venv $VENV
pip install -e /opt/hin
chown -R $USER:$USER ./
EOF
USER $USER

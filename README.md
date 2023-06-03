# Bluelog

*A blue blog.*

> Example application for *[Python Web Development with Flask](https://helloflask.com/en/book/1)* (《[Flask Web 开发实战](https://helloflask.com/book/1)》).

Demo: http://bluelog.helloflask.com

![Screenshot](https://helloflask.com/screenshots/bluelog.png)

## Installation

Clone the repo:

```
$ git clone https://github.com/greyli/new-bluelog.git
$ cd new-bluelog
```

Create & activate virtual env then install dependency:

with venv + pip:

```
$ python3 -m venv .venv  # use `python ...` on Windows
$ source .venv/bin/activate  # use `.venv\Scripts\activate` on Windows
$ pip install -r requirements.txt
```

or with PDM (you need to [install PDM](https://pdm.fming.dev/latest/#installation) first):

```
$ pdm install
$ source .venv/bin/activate  # use `.venv\Scripts\activate` on Windows
```

Generate fake data then run the application:

```
$ flask fake
$ flask run
* Running on http://127.0.0.1:5000/
```

Test account:

* username: `admin`
* password: `helloflask`

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).

# Greybook

> Example application for *[Python Web Development with Flask](https://helloflask.com/en/book/1)* (《[Flask Web 开发实战](https://helloflask.com/book/4)》).

Demo: http://greybook.helloflask.com

![Screenshot](https://helloflask.com/screenshots/greybook.png)

## Installation

Clone the repo:

```
$ git clone https://github.com/greyli/greybook.git
$ cd greybook
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
$ flask lorem
$ flask run
* Running on http://127.0.0.1:5000/
```

Test account:

* username: `admin`
* password: `greybook`

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).

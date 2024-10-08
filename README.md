# **ArcLog**

_Structured Python logging <sup>(for the Arcane 🧙🏼‍♂️)</sup>._

This project is essentially just my personal logging configuration, which I aim
to make into a small library of sorts.

## Features (Planned)

- [ ] JSON logs for structured logging output.
- [x] Implementation of [`functools.singledispatch`] for performant and
      efficient encoding of a wide variety of Python data types.
- [ ] Integration with [`structlog`] for flexible and powerful logging.
- [ ] Support for [`msgspec`], including `msgspec.Struct` `LogRecord` objects
      for efficient serialization.
- [ ] Borrowed code and ideas from other great projects, like
      [`python-json-logger`] and [`litestar`].
- [ ] ???

## Getting Started

This project is still in the early stages of development. Stay tuned for
installation instructions and usage examples.

## License

This project is licensed under the [Apache-2.0] License.

[`msgspec`]: https://jcristharif.com/msgspec/
[`structlog`]: https://www.structlog.org/en/stable/index.html
[`litestar`]: https://github.com/litestar-org/litestar
[`python-json-logger`]: https://github.com/nhairs/python-json-logger
[apache-2.0]: /LICENSE.txt
[`functools.singledispatch`]:
  https://docs.python.org/3/library/functools.html#functools.singledispatch


# Multi-asset lightning demo

The main goal is to succesfully route lightning payments through
channels with different chain_hash and thus representing different
assets.

A daemon that is able to operate an arbitrary number of different
chains is convenient and thus a custom branch will be used instead of
a released bitcoin version already compiled.

# Future work

- Route through channels in chains with multiple assets
- Route through channels in chains with a single asset but with CT
- Route through channels in chains with CT/CA

### License

MIT, see COPYING

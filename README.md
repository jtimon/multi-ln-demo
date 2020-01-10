
# Multi-asset lightning demo

The main goal is to succesfully route lightning payments through
channels with different chain_hash and thus representing different
assets.

A daemon that is able to operate an arbitrary number of different
chains is convenient and thus a custom branch will be used instead of
a released bitcoin version already compiled.

# Dependencies

docker and docker-compose.
See https://docs.docker.com/compose/install/

# Run

See Makefile and docker-compose documentation

# Incremental goals

- [x] 2 chains, 1 asset (non atomic, trusted)
- [x] 2 chains, 2 asset (non atomic, trusted)
- [ ] 2 chains, 1 asset (atomic, trustless)
- [ ] 2 chains, 2 asset
- [ ] N chains, N assets
- [ ] 1 chain, 2 assets
- [ ] 1 chain, M assets
- [ ] N chains, M assets
- [ ] With CT/CA

# First goal: pay between two chains

- Alice, with channels opened only on regtest
- Carol with channels opened only on liquid-regtest

Alice should be able to pay an invoice from Carol, even though the invoice is for liquid-regtest

The pricing between chains/assets is always 1:1 for now for simplicity.

## Plan A: Gateways

A gateway is a server controlling 2 or more "sibling nodes" which
connect to different networks and is willing to route payments through
them under its own criteria.

- Bob has a gateway
- Bob's gateway has channels opened on both regtest and liquid-regtest

## Step A.1: Non atomic routing

The payer trusts the gateway will pay invoice_dest_chain if it pays
invoice_src_chain to the gateway.

Gateways are configured manually by users somehow, there's no protocol
or extension of existing protocol for gateway users to automatically
discover gateway servers.

Supposedly, the gateway won't be a scammer because otherwise it will
lose reputation points or something (see step A.2).

## TODO Step A.2: Both invoices are paid or not atomically

The payer doesn't risk to pay invoice_src_chain to the gateway unless it is guaranteed
that implies invoice_dest_chain is or will be paid by the gateway too.

# Future work (aka out of scope for this demo)

- Route through channels in chains with multiple assets
- Route through channels in chains with a single asset but with CT
- Route through channels in chains with CT/CA

### License

MIT, see COPYING

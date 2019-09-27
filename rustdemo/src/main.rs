
#[derive(Debug)]
struct RpcCaller {
    addr: String,
    user: String,
    pass: String,
}

#[derive(Debug)]
struct ChainConfig {
    port_decimal: u32,
    users: Vec<String>,
}

fn main() {
    println!("This is a demo demonstrating a lightning payments across 2 different chains");

    let mut chains = std::collections::HashMap::new();

    chains.insert("chain_1", ChainConfig {
        port_decimal: 4,
        users: vec![String::from("alice"), String::from("bob")],
    });
    chains.insert("chain_2", ChainConfig {
        port_decimal: 5,
        users: vec![String::from("bob"), String::from("carol")],
    });

    println!("Chains considered (with their users): {:?}", chains);

    let mut bitcoinds = std::collections::HashMap::new();
    for (chain_name, chain_config) in chains.iter() {

        let mut bitcoinds_for_chain = std::collections::HashMap::new();
        for user in chain_config.users.iter() {
            let rpc_port = format!("185{}5", chain_config.port_decimal);
            bitcoinds_for_chain.insert(user, RpcCaller {
                addr: format!("0.0.0.0:{}", rpc_port),
                user: format!("user{}", rpc_port),
                pass: format!("password{}", rpc_port),
            });
        }
        bitcoinds.insert(chain_name, bitcoinds_for_chain);
    }
    println!("Bitcoind instances to connect to: {:?}", bitcoinds);

    // Wait for daemons to start
    std::thread::sleep(std::time::Duration::from_secs(5));

    println!("All done. Exiting in 5 seconds...");
    std::thread::sleep(std::time::Duration::from_secs(5));
}

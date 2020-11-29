async function pushTransaction(transaction) {
    try {
        const response = await fetch(process.env.transactionApi, {
            method: 'POST',
            headers: {  'Content-Type': 'application/json'},
            body: JSON.stringify({
                "username": process.env.username,
                "password":process.env.password,
                "transaction": transaction})
        });
        responseLog = {
            status: response.status,
            statusText: response.statusText,
            serverMessage: (await response.text())
        }
        console.log(JSON.stringify(responseLog))
    }
    catch (e) {
        console.log(e)
    }
};

// This function runs during the card transaction authorization flow.
// It has a limited execution time, so keep any code short-running.
const beforeTransaction = async (authorization) => {
    return true;
};

// This function runs after a transaction.
const afterTransaction = async (transaction) => {
    if (transaction.reference === 'simulation') {
        // this is a simulated transaction
        await pushTransaction(transaction)
    }
    else {
        // this is a production transaction
    }
};

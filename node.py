import json
from blockchain import BlockChain
from flask import Flask, jsonify, request
from textwrap import dedent
from uuid import uuid4


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
bc = BlockChain()


@app.route('/mine', methods=['POST'])
def mine():
    last_block = bc.last_block
    # We run the proof of work algorithm to get the next proof...
    old_proof = last_block['proof']
    proof = bc.proof_of_work(old_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    bc.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    # Forge the new Block by adding it to the chain
    previous_hash = bc.hash(last_block)
    block = bc.new_block(previous_hash=previous_hash, proof=proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200




@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = bc.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}


    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': bc.chain,
        'length': len(bc.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


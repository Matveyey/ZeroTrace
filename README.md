# ZeroTrace: Quantum-Resistant Secure Messenger

## Description

ZeroTrace is a secure messenger designed to counter threats posed by quantum computing. Traditional cryptographic protocols, such as RSA and ECC, are vulnerable to quantum algorithms like Shor's algorithm. ZeroTrace addresses this issue by implementing post-quantum cryptographic algorithms to ensure confidentiality, integrity, and security of communications.

The primary goal of ZeroTrace is to develop and analyze a prototype messenger using post-quantum algorithms. Project objectives include:
- Studying and selecting effective post-quantum cryptography standards (e.g., NIST recommendations).
- Designing an architecture for secure message exchange using key encapsulation mechanisms (KEM) and digital signatures.
- Implementing a prototype with end-to-end encryption (E2EE), decentralization, and protection against quantum attacks.
- Testing algorithm performance and evaluating their real-time applicability.

## Features

- **Post-Quantum Security**: Utilizes Kyber512 for key encapsulation and Dilithium for digital signatures, as recommended by NIST.
- **End-to-End Encryption (E2EE)**: Ensures that only the sender and recipient can access message content.
- **Decentralization**: Enhances resilience against censorship and central server failures.
- **User Anonymity**: Users are identified via public key hashes, eliminating the need for personal identifiers.

## Architecture

ZeroTrace employs a client-server model:
- **Client**: Handles key generation, storage, encryption/decryption, and server interaction. Implemented in Python using the Flet framework.
- **Server**: Manages user authentication, stores public keys, and facilitates message exchange via REST API (FastAPI). Data is stored in MongoDB.

Future plans include transitioning to a peer-to-peer (P2P) model to support offline functionality and reduce server dependency.

## Cryptographic Algorithms

| Algorithm  | Purpose                      | Description                                                              |
|------------|------------------------------|--------------------------------------------------------------------------|
| Kyber512   | Key Encapsulation (KEM)      | Post-quantum algorithm for secure key exchange based on LWE.             |
| Dilithium  | Digital Signature            | Post-quantum algorithm for message authentication.                       |
| AES-GCM    | Symmetric Encryption         | Used for encrypting message content after key exchange.                  |

## Implementation Details

- **Interface Framework**: Flet (Python-based, cross-platform).
- **Server**: FastAPI.
- **Databases**: MongoDB (server-side), SQLite (client-side local storage).
- **Cryptography**: oqs-python library for post-quantum cryptography.

## Performance

Tested on Intel Core i5-12600, 16 GB RAM, Nvidia RTX 3060, Windows 10. Average operation times:

| Operation                           | Time (sec) |
|-------------------------------------|------------|
| Kyber512 (encapsulation/decapsulation) | 0.9        |
| Dilithium (signing/verification)    | 0.5 / 0.2  |
| AES-GCM (encryption/decryption)     | 0.3–0.9    |
| Message send/receive (API)          | 0.5–0.5    |

Total message sending latency: 1–2 seconds, suitable for real-time communication.

## Security Measures

- Protection against quantum attacks, man-in-the-middle (MitM) attacks, server compromise, key loss, DoS attacks, and social engineering.
- Use of digital signatures and unique dialog hashes to ensure authenticity and integrity.
- Minimization of metadata exposure through hashed identifiers and plans for a federated architecture.

## Comparison with Existing Solutions

ZeroTrace stands out compared to Signal, Threema, and Matrix due to:
- Resilience against quantum attacks.
- Decentralized architecture.
- Open-source code.
- Anonymity via hashed identifiers.

## Future Plans

- Transition to a fully decentralized P2P architecture.
- Improved user education on key management.
- Enhanced scalability for DoS attack protection.

## Dependencies

- oqs-python (post-quantum cryptography)
- FastAPI (server)
- MongoDB (database)
- SQLite (local storage)
- Flet (interface)

## License

ZeroTrace is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, provided the following conditions are met:

- The copyright notice and this permission notice must be included in all copies or substantial portions of the software.
- The software is provided "as is," without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and noninfringement.

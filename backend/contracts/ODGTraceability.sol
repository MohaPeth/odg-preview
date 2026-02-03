// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ODGTraceability
 * @dev Smart contract pour la traçabilité des matériaux miniers ODG
 * 
 * Ce contrat permet d'enregistrer de manière immuable les hash des transactions
 * de traçabilité des matériaux (or, diamant, manganèse, etc.) sur la blockchain.
 * 
 * Chaque enregistrement contient :
 * - Un hash unique de la transaction (généré côté backend)
 * - Le type de matériau
 * - La quantité
 * - L'horodatage blockchain
 * - L'adresse de l'émetteur
 */
contract ODGTraceability {
    
    // Structure d'un enregistrement de traçabilité
    struct TraceRecord {
        bytes32 transactionHash;    // Hash unique de la transaction
        string materialType;         // Type de matériau (Or, Diamant, etc.)
        uint256 quantity;            // Quantité en grammes (multiplié par 1000 pour précision)
        uint256 timestamp;           // Horodatage de l'enregistrement
        address recorder;            // Adresse qui a enregistré
        string origin;               // Origine du matériau
        string destination;          // Destination
        bool isValid;                // Statut de validité
    }
    
    // Mapping des enregistrements par hash
    mapping(bytes32 => TraceRecord) public records;
    
    // Liste des hash pour itération
    bytes32[] public recordHashes;
    
    // Adresse du propriétaire du contrat
    address public owner;
    
    // Adresses autorisées à enregistrer
    mapping(address => bool) public authorizedRecorders;
    
    // Événements
    event RecordCreated(
        bytes32 indexed transactionHash,
        string materialType,
        uint256 quantity,
        uint256 timestamp,
        address indexed recorder
    );
    
    event RecordInvalidated(
        bytes32 indexed transactionHash,
        address indexed invalidatedBy,
        uint256 timestamp
    );
    
    event RecorderAuthorized(address indexed recorder);
    event RecorderRevoked(address indexed recorder);
    
    // Modificateurs
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            authorizedRecorders[msg.sender] || msg.sender == owner,
            "Not authorized to record"
        );
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedRecorders[msg.sender] = true;
    }
    
    /**
     * @dev Autorise une adresse à enregistrer des transactions
     * @param _recorder Adresse à autoriser
     */
    function authorizeRecorder(address _recorder) external onlyOwner {
        authorizedRecorders[_recorder] = true;
        emit RecorderAuthorized(_recorder);
    }
    
    /**
     * @dev Révoque l'autorisation d'une adresse
     * @param _recorder Adresse à révoquer
     */
    function revokeRecorder(address _recorder) external onlyOwner {
        authorizedRecorders[_recorder] = false;
        emit RecorderRevoked(_recorder);
    }
    
    /**
     * @dev Enregistre une nouvelle transaction de traçabilité
     * @param _transactionHash Hash unique de la transaction
     * @param _materialType Type de matériau
     * @param _quantity Quantité (en grammes * 1000)
     * @param _origin Origine du matériau
     * @param _destination Destination
     */
    function createRecord(
        bytes32 _transactionHash,
        string memory _materialType,
        uint256 _quantity,
        string memory _origin,
        string memory _destination
    ) external onlyAuthorized {
        require(records[_transactionHash].timestamp == 0, "Record already exists");
        require(_quantity > 0, "Quantity must be positive");
        
        TraceRecord memory newRecord = TraceRecord({
            transactionHash: _transactionHash,
            materialType: _materialType,
            quantity: _quantity,
            timestamp: block.timestamp,
            recorder: msg.sender,
            origin: _origin,
            destination: _destination,
            isValid: true
        });
        
        records[_transactionHash] = newRecord;
        recordHashes.push(_transactionHash);
        
        emit RecordCreated(
            _transactionHash,
            _materialType,
            _quantity,
            block.timestamp,
            msg.sender
        );
    }
    
    /**
     * @dev Invalide un enregistrement (ne le supprime pas, marque comme invalide)
     * @param _transactionHash Hash de la transaction à invalider
     */
    function invalidateRecord(bytes32 _transactionHash) external onlyOwner {
        require(records[_transactionHash].timestamp != 0, "Record does not exist");
        require(records[_transactionHash].isValid, "Record already invalidated");
        
        records[_transactionHash].isValid = false;
        
        emit RecordInvalidated(_transactionHash, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Vérifie si un enregistrement existe et est valide
     * @param _transactionHash Hash à vérifier
     * @return exists Si l'enregistrement existe
     * @return isValid Si l'enregistrement est valide
     */
    function verifyRecord(bytes32 _transactionHash) 
        external 
        view 
        returns (bool exists, bool isValid) 
    {
        TraceRecord memory record = records[_transactionHash];
        exists = record.timestamp != 0;
        isValid = record.isValid;
    }
    
    /**
     * @dev Récupère les détails d'un enregistrement
     * @param _transactionHash Hash de la transaction
     */
    function getRecord(bytes32 _transactionHash) 
        external 
        view 
        returns (
            string memory materialType,
            uint256 quantity,
            uint256 timestamp,
            address recorder,
            string memory origin,
            string memory destination,
            bool isValid
        ) 
    {
        TraceRecord memory record = records[_transactionHash];
        require(record.timestamp != 0, "Record does not exist");
        
        return (
            record.materialType,
            record.quantity,
            record.timestamp,
            record.recorder,
            record.origin,
            record.destination,
            record.isValid
        );
    }
    
    /**
     * @dev Retourne le nombre total d'enregistrements
     */
    function getTotalRecords() external view returns (uint256) {
        return recordHashes.length;
    }
    
    /**
     * @dev Récupère un hash par index (pour pagination)
     * @param _index Index dans la liste
     */
    function getRecordHashByIndex(uint256 _index) external view returns (bytes32) {
        require(_index < recordHashes.length, "Index out of bounds");
        return recordHashes[_index];
    }
    
    /**
     * @dev Transfère la propriété du contrat
     * @param _newOwner Nouvelle adresse propriétaire
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Invalid address");
        owner = _newOwner;
    }
}

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Shield, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Link,
  QrCode,
  Download,
  Eye,
  Hash,
  Coins
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

// Données simulées pour les graphiques
const transactionData = [
  { date: '2025-01-01', transactions: 12, volume: 45.2 },
  { date: '2025-01-02', transactions: 18, volume: 67.8 },
  { date: '2025-01-03', transactions: 15, volume: 52.1 },
  { date: '2025-01-04', transactions: 22, volume: 89.3 },
  { date: '2025-01-05', transactions: 19, volume: 71.5 },
  { date: '2025-01-06', transactions: 25, volume: 95.7 },
  { date: '2025-01-07', transactions: 21, volume: 78.9 }
];

const materialDistribution = [
  { name: 'Or', value: 75, color: '#FFD700' },
  { name: 'Diamant', value: 20, color: '#87CEEB' },
  { name: 'Autres', value: 5, color: '#DDA0DD' }
];

const statusDistribution = [
  { name: 'Confirmées', value: 68, color: '#22c55e' },
  { name: 'En attente', value: 25, color: '#eab308' },
  { name: 'Échouées', value: 7, color: '#ef4444' }
];

// Données de démonstration pour le mode mock si l'API blockchain est indisponible
const demoTransactions = [
  {
    id: 1,
    transactionHash: '0xabc1234567890abcdef1234567890abcdef1234',
    blockNumber: 1234567,
    fromAddress: '0xFROMADDRESS000000000000000000000000000001',
    toAddress: '0xTOADDRESS00000000000000000000000000000001',
    materialType: 'Or',
    quantity: 10.5,
    unit: 'kg',
    timestamp: new Date().toISOString(),
    status: 'confirmed',
    metadata: {
      origin: 'Mine Minkebe',
      destination: 'Raffinerie Libreville',
      lot: 'LOT-OR-0001',
    },
  },
  {
    id: 2,
    transactionHash: '0xdef9876543210abcdef9876543210abcdef9876',
    blockNumber: 1234568,
    fromAddress: '0xFROMADDRESS000000000000000000000000000002',
    toAddress: '0xTOADDRESS00000000000000000000000000000002',
    materialType: 'Diamant',
    quantity: 120,
    unit: 'carats',
    timestamp: new Date().toISOString(),
    status: 'pending',
    metadata: {
      origin: 'Mine Franceville',
      destination: 'Centre de tri',
      lot: 'LOT-DIA-0003',
    },
  },
  {
    id: 3,
    transactionHash: '0x1234567890abcdef1234567890abcdef1234567',
    blockNumber: 1234569,
    fromAddress: '0xFROMADDRESS000000000000000000000000000003',
    toAddress: '0xTOADDRESS00000000000000000000000000000003',
    materialType: 'Manganèse',
    quantity: 850,
    unit: 'tonnes',
    timestamp: new Date().toISOString(),
    status: 'confirmed',
    metadata: {
      origin: 'Mine Moanda',
      destination: 'Port Owendo',
      lot: 'LOT-MN-0010',
    },
  },
];

const demoCertificates = [
  {
    id: 'CERT-000001',
    transactionHash: demoTransactions[0].transactionHash,
    materialType: demoTransactions[0].materialType,
    quantity: demoTransactions[0].quantity,
    unit: demoTransactions[0].unit,
    origin: 'Mine Minkebe',
    destination: 'Raffinerie Libreville',
    certificationDate: demoTransactions[0].timestamp,
  },
  {
    id: 'CERT-000003',
    transactionHash: demoTransactions[2].transactionHash,
    materialType: demoTransactions[2].materialType,
    quantity: demoTransactions[2].quantity,
    unit: demoTransactions[2].unit,
    origin: 'Mine Moanda',
    destination: 'Port Owendo',
    certificationDate: demoTransactions[2].timestamp,
  },
];

const demoStats = {
  transactions: {
    total: demoTransactions.length,
    confirmed: demoTransactions.filter((t) => t.status === 'confirmed').length,
    pending: demoTransactions.filter((t) => t.status === 'pending').length,
  },
  materials: [
    {
      type: 'Or',
      transactions: 1,
      totalQuantity: 10.5,
    },
    {
      type: 'Diamant',
      transactions: 1,
      totalQuantity: 120,
    },
    {
      type: 'Manganèse',
      transactions: 1,
      totalQuantity: 850,
    },
  ],
  totalVolume: 10.5 + 120 + 850,
  certificates: demoCertificates.length,
};

const BlockchainDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTransaction, setSelectedTransaction] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Récupération des transactions
      const transactionsResponse = await fetch('/api/blockchain/transactions');
      const transactionsData = await transactionsResponse.json();
      
      // Récupération des certificats
      const certificatesResponse = await fetch('/api/blockchain/certificates');
      const certificatesData = await certificatesResponse.json();
      
      // Récupération des statistiques
      const statsResponse = await fetch('/api/blockchain/stats');
      const statsData = await statsResponse.json();
      
      if (transactionsData.success) setTransactions(transactionsData.data);
      if (certificatesData.success) setCertificates(certificatesData.data);
      if (statsData.success) setStats(statsData.data);
      
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      // Mode démonstration : utiliser des données mock si l'API est indisponible
      setTransactions(demoTransactions);
      setCertificates(demoCertificates);
      setStats(demoStats);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'confirmed':
        return 'Confirmée';
      case 'pending':
        return 'En attente';
      case 'failed':
        return 'Échouée';
      default:
        return 'Inconnu';
    }
  };

  const filteredTransactions = transactions.filter(tx =>
    tx.transactionHash.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.materialType.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.fromAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.toAddress.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateHash = (hash) => {
    return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
            <Shield className="mr-3 h-8 w-8 text-blue-600" />
            Tableau de Bord Blockchain ODG
          </h1>
          <p className="text-gray-600">
            Système de traçabilité et de transparence pour les activités minières
          </p>
        </div>

        {/* Statistiques principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Transactions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats.transactions?.total || 0}
                  </p>
                </div>
                <Hash className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Confirmées</p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.transactions?.confirmed || 0}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">En Attente</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {stats.transactions?.pending || 0}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Volume Total</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {stats.totalVolume || 0} kg
                  </p>
                </div>
                <Coins className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Graphiques */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Évolution des Transactions</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={transactionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="transactions" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="Transactions"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Distribution par Matériau</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={materialDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {materialDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Onglets principaux */}
        <Tabs defaultValue="transactions" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
            <TabsTrigger value="certificates">Certificats</TabsTrigger>
            <TabsTrigger value="supply-chain">Chaîne d'Approvisionnement</TabsTrigger>
          </TabsList>

          {/* Onglet Transactions */}
          <TabsContent value="transactions">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Transactions Blockchain</CardTitle>
                  <div className="flex space-x-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Rechercher par hash, matériau, adresse..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 w-80"
                      />
                    </div>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Exporter
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredTransactions.map((tx) => (
                    <div
                      key={tx.id}
                      className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedTransaction(tx)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getStatusColor(tx.status)} text-white`}>
                            {getStatusText(tx.status)}
                          </Badge>
                          <span className="font-mono text-sm text-gray-600">
                            {truncateHash(tx.transactionHash)}
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {formatDate(tx.timestamp)}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Matériau:</span>
                          <span className="ml-2">{tx.materialType}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Quantité:</span>
                          <span className="ml-2">{tx.quantity} {tx.unit}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Bloc:</span>
                          <span className="ml-2">#{tx.blockNumber}</span>
                        </div>
                      </div>
                      
                      <div className="mt-2 text-sm">
                        <div className="flex items-center space-x-4">
                          <span>
                            <span className="font-medium text-gray-700">De:</span>
                            <span className="ml-2 font-mono">{truncateHash(tx.fromAddress)}</span>
                          </span>
                          <span>→</span>
                          <span>
                            <span className="font-medium text-gray-700">Vers:</span>
                            <span className="ml-2 font-mono">{truncateHash(tx.toAddress)}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Onglet Certificats */}
          <TabsContent value="certificates">
            <Card>
              <CardHeader>
                <CardTitle>Certificats de Traçabilité</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {certificates.map((cert) => (
                    <Card key={cert.id} className="border-l-4 border-l-green-500">
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <CardTitle className="text-lg">{cert.id}</CardTitle>
                          <Badge className="bg-green-500 text-white">Valide</Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <span className="font-medium text-gray-700">Matériau:</span>
                          <span className="ml-2">{cert.materialType}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Quantité:</span>
                          <span className="ml-2">{cert.quantity} {cert.unit}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Origine:</span>
                          <span className="ml-2">{cert.origin}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Destination:</span>
                          <span className="ml-2">{cert.destination}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Date:</span>
                          <span className="ml-2">{formatDate(cert.certificationDate)}</span>
                        </div>
                        <div className="flex space-x-2 pt-2">
                          <Button size="sm" variant="outline">
                            <QrCode className="h-4 w-4 mr-2" />
                            QR Code
                          </Button>
                          <Button size="sm" variant="outline">
                            <Eye className="h-4 w-4 mr-2" />
                            Détails
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Onglet Chaîne d'Approvisionnement */}
          <TabsContent value="supply-chain">
            <Card>
              <CardHeader>
                <CardTitle>Chaîne d'Approvisionnement</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="flex items-center space-x-4">
                    <Input placeholder="Rechercher par type de matériau..." className="max-w-md" />
                    <Button>
                      <Search className="h-4 w-4 mr-2" />
                      Rechercher
                    </Button>
                  </div>
                  
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4">Traçabilité de l'Or - Mine Minkebe</h3>
                    <div className="space-y-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">1</div>
                        <div className="flex-1">
                          <h4 className="font-medium">Extraction</h4>
                          <p className="text-sm text-gray-600">Mine Minkebe - 10.5 kg d'or extrait</p>
                          <p className="text-xs text-gray-500">2025-07-11 14:55</p>
                        </div>
                        <Badge className="bg-green-500 text-white">Confirmé</Badge>
                      </div>
                      
                      <div className="ml-4 border-l-2 border-gray-300 h-8"></div>
                      
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">2</div>
                        <div className="flex-1">
                          <h4 className="font-medium">Transport</h4>
                          <p className="text-sm text-gray-600">Vers Raffinerie Libreville</p>
                          <p className="text-xs text-gray-500">Impact CO2: 2.1 tonnes</p>
                        </div>
                        <Badge className="bg-green-500 text-white">Confirmé</Badge>
                      </div>
                      
                      <div className="ml-4 border-l-2 border-gray-300 h-8"></div>
                      
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold">3</div>
                        <div className="flex-1">
                          <h4 className="font-medium">Raffinage</h4>
                          <p className="text-sm text-gray-600">Purification à 99.5%</p>
                          <p className="text-xs text-gray-500">En cours...</p>
                        </div>
                        <Badge className="bg-yellow-500 text-white">En cours</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Modal de détails de transaction */}
        {selectedTransaction && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Détails de la Transaction</CardTitle>
                  <Button
                    variant="ghost"
                    onClick={() => setSelectedTransaction(null)}
                  >
                    ×
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <span className="font-medium text-gray-700">Hash de Transaction:</span>
                  <p className="font-mono text-sm bg-gray-100 p-2 rounded mt-1">
                    {selectedTransaction.transactionHash}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="font-medium text-gray-700">Statut:</span>
                    <Badge className={`ml-2 ${getStatusColor(selectedTransaction.status)} text-white`}>
                      {getStatusText(selectedTransaction.status)}
                    </Badge>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Bloc:</span>
                    <span className="ml-2">#{selectedTransaction.blockNumber}</span>
                  </div>
                </div>
                
                <div>
                  <span className="font-medium text-gray-700">Adresse Expéditeur:</span>
                  <p className="font-mono text-sm bg-gray-100 p-2 rounded mt-1">
                    {selectedTransaction.fromAddress}
                  </p>
                </div>
                
                <div>
                  <span className="font-medium text-gray-700">Adresse Destinataire:</span>
                  <p className="font-mono text-sm bg-gray-100 p-2 rounded mt-1">
                    {selectedTransaction.toAddress}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="font-medium text-gray-700">Matériau:</span>
                    <span className="ml-2">{selectedTransaction.materialType}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Quantité:</span>
                    <span className="ml-2">{selectedTransaction.quantity} {selectedTransaction.unit}</span>
                  </div>
                </div>
                
                <div>
                  <span className="font-medium text-gray-700">Timestamp:</span>
                  <span className="ml-2">{formatDate(selectedTransaction.timestamp)}</span>
                </div>
                
                {selectedTransaction.metadata && Object.keys(selectedTransaction.metadata).length > 0 && (
                  <div>
                    <span className="font-medium text-gray-700">Métadonnées:</span>
                    <pre className="text-sm bg-gray-100 p-2 rounded mt-1 overflow-x-auto">
                      {JSON.stringify(selectedTransaction.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default BlockchainDashboard;


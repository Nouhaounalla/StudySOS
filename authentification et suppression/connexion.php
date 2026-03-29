<?php
require_once 'config.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Méthode non autorisée.']);
    exit;
}
$email    = trim(strtolower($_POST['email']    ?? ''));
$password = $_POST['mot_de_passe'] ?? '';
if (empty($email) || empty($password)) {
    echo json_encode(['success' => false, 'message' => 'Email et mot de passe requis.']);
    exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['success' => false, 'message' => 'Format d\'email invalide.']);
    exit;
}
$pdo  = getDB();
$stmt = $pdo->prepare("
    SELECT id, prenom, nom, mot_de_passe, role
    FROM utilisateurs
    WHERE email = ?
    LIMIT 1
");
$stmt->execute([$email]);
$user = $stmt->fetch(); // Retourne un tableau associatif ou false si introuvable
if (!$user) {
    echo json_encode([
        'success' => false,
        'message' => 'Email ou mot de passe incorrect.'
    ]);
    exit;
}
if (!password_verify($password, $user['mot_de_passe'])) {
    echo json_encode([
        'success' => false,
        'message' => 'Email ou mot de passe incorrect.'
    ]);
    exit;
}
session_regenerate_id(true);
$_SESSION['user_id'] = (int) $user['id'];
$_SESSION['role']    = $user['role'];
$_SESSION['nom']     = $user['prenom'] . ' ' . $user['nom'];
$redirections = [
    'admin'    => 'dashboard_admin.php',
    'tuteur'   => 'dashboard_tuteur.php',
    'etudiant' => 'dashboard_etudiant.php',
];
echo json_encode([
    'success'  => true,
    'message'  => 'Connexion réussie ! Bienvenue ' . $user['prenom'] ,
    'redirect' => $redirections[$user['role']] ?? 'auth.html'
]);

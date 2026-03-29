<?php
require_once 'config.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Méthode non autorisée.']);
    exit;
}
$prenom   = trim(htmlspecialchars($_POST['prenom']      ?? ''));
$nom      = trim(htmlspecialchars($_POST['nom']         ?? ''));
$email    = trim(strtolower($_POST['email']             ?? ''));
$password = $_POST['mot_de_passe'] ?? '';  
$role     = $_POST['role']         ?? 'etudiant';
$erreurs = [];
if (strlen($prenom) < 2)
    $erreurs[] = 'Le prénom doit contenir au moins 2 caractères.';
if (strlen($nom) < 2)
    $erreurs[] = 'Le nom doit contenir au moins 2 caractères.';
if (!filter_var($email, FILTER_VALIDATE_EMAIL))
    $erreurs[] = 'Adresse email invalide.';
if (strlen($password) < 8)
    $erreurs[] = 'Le mot de passe doit contenir au moins 8 caractères.';
if (!preg_match('/[A-Z]/', $password))
    $erreurs[] = 'Le mot de passe doit contenir au moins une majuscule.';
if (!preg_match('/[0-9]/', $password))
    $erreurs[] = 'Le mot de passe doit contenir au moins un chiffre.';
if (!in_array($role, ['etudiant', 'tuteur']))
    $erreurs[] = 'Rôle invalide.';
if (!empty($erreurs)) {
    echo json_encode(['success' => false, 'message' => implode(' ', $erreurs)]);
    exit;
}
$pdo  = getDB();
$stmt = $pdo->prepare("SELECT id FROM utilisateurs WHERE email = ? LIMIT 1");
$stmt->execute([$email]);
if ($stmt->fetch()) {
    echo json_encode([
        'success' => false,
        'message' => 'Cette adresse email est déjà utilisée. Connectez-vous ou utilisez un autre email.'
    ]);
    exit;
}
$hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
try {
    $stmt = $pdo->prepare("
        INSERT INTO utilisateurs (prenom, nom, email, mot_de_passe, role)
        VALUES (?, ?, ?, ?, ?)
    ");
    $stmt->execute([$prenom, $nom, $email, $hash, $role]);
    $newId = (int) $pdo->lastInsertId();
    session_regenerate_id(true);
    $_SESSION['user_id'] = $newId;
    $_SESSION['role']    = $role;
    $_SESSION['nom']     = $prenom . ' ' . $nom;
    $redirect = ($role === 'tuteur') ? 'dashboard_tuteur.php' : 'dashboard_etudiant.php';
    echo json_encode([
        'success'  => true,
        'message'  => "Compte créé avec succès ! Bienvenue $prenom",
        'redirect' => $redirect
    ]);
} catch (PDOException $e) {
    error_log('[Inscription] ' . $e->getMessage());
    echo json_encode(['success' => false, 'message' => 'Erreur serveur. Réessayez plus tard.']);
}

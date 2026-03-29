<?php
require_once 'config.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Méthode non autorisée.']);
    exit;
}
$pdo = getDB();
if (!empty($_SESSION['user_id']) && $_SESSION['role'] === 'admin' && !empty($_POST['user_id'])) {
    $targetId = (int) $_POST['user_id'];
    $stmt = $pdo->prepare("SELECT id, prenom, nom FROM utilisateurs WHERE id = ?");
    $stmt->execute([$targetId]);
    $cible = $stmt->fetch();
    if (!$cible) {
        echo json_encode(['success' => false, 'message' => 'Compte introuvable.']);
        exit;
    }
    $stmt = $pdo->prepare("DELETE FROM utilisateurs WHERE id = ?");
    $stmt->execute([$targetId]);
    if ($stmt->rowCount() === 0) {
        echo json_encode(['success' => false, 'message' => 'Suppression échouée.']);
        exit;
    }
    echo json_encode([
        'success' => true,
        'message' => "Le compte de {$cible['prenom']} {$cible['nom']} a été supprimé définitivement."
    ]);
    exit;
}
$email    = trim(strtolower($_POST['email']    ?? ''));
$password = $_POST['mot_de_passe'] ?? '';
$confirme = isset($_POST['confirme']) && $_POST['confirme'] === 'on';
if (empty($email) || empty($password)) {
    echo json_encode(['success' => false, 'message' => 'Email et mot de passe requis.']);
    exit;
}
if (!$confirme) {
    echo json_encode(['success' => false, 'message' => 'Vous devez cocher la case de confirmation.']);
    exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['success' => false, 'message' => 'Format d\'email invalide.']);
    exit;
}
$stmt = $pdo->prepare("
    SELECT id, prenom, nom, mot_de_passe
    FROM utilisateurs
    WHERE email = ?
    LIMIT 1
");
$stmt->execute([$email]);
$user = $stmt->fetch();
if (!$user) {
    echo json_encode(['success' => false, 'message' => 'Aucun compte trouvé avec cet email.']);
    exit;
}
if (!password_verify($password, $user['mot_de_passe'])) {
    echo json_encode(['success' => false, 'message' => 'Mot de passe incorrect. Suppression annulée.']);
    exit;
}
try {
    $stmt = $pdo->prepare("DELETE FROM utilisateurs WHERE id = ?");
    $stmt->execute([$user['id']]);

    if ($stmt->rowCount() === 0) {
        echo json_encode(['success' => false, 'message' => 'Erreur : aucun compte supprimé.']);
        exit;
    }
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000,
            $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();

    echo json_encode([
        'success'  => true,
        'message'  => "Votre compte a été supprimé définitivement. Au revoir {$user['prenom']} !",
        'redirect' => 'auth.html'  
    ]);
} catch (PDOException $e) {
    error_log('[Suppression] ' . $e->getMessage());
    echo json_encode(['success' => false, 'message' => 'Erreur serveur lors de la suppression.']);
}

const express = require('express');
const router = express.Router();
const { loginAdmin, verifyAdminToken } = require('../middleware/auth');

// Authentication endpoints (no auth required)
router.post('/login', async (req, res) => {
  try {
    const { password } = req.body;

    if (!password) {
      return res.status(400).json({ error: 'Password is required' });
    }

    const { token, expiresIn } = await loginAdmin(password);
    res.json({ token, expires_in: expiresIn });
  } catch (error) {
    res.status(401).json({ error: 'Invalid password' });
  }
});

router.post('/verify', verifyAdminToken, (req, res) => {
  // If this route is reached, the token is valid (checked by middleware)
  res.json({ valid: true });
});

module.exports = router;

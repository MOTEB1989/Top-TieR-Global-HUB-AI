module.exports = (req, res, next) => {
  if (req.body && JSON.stringify(req.body).length > 10 * 1024 * 1024) {
    return res.status(413).json({ error: "Too large" });
  }
  next();
};

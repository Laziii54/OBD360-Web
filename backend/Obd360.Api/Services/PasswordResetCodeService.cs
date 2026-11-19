using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Obd360.Api.Services;

public sealed record PasswordResetCodeResult(bool Success, string? Token, string? Error);

public interface IPasswordResetCodeService
{
    void Store(string email, string code, string resetToken);

    PasswordResetCodeResult Validate(string email, string code);

    void Remove(string email);
}

public sealed class PasswordResetCodeService : IPasswordResetCodeService
{
    private static readonly TimeSpan Lifetime = TimeSpan.FromMinutes(10);
    private const int MaxAttempts = 5;
    private const string KeyPrefix = "password-reset:";

    private readonly ILogger<PasswordResetCodeService> _logger;
    private readonly object _fileLock = new();
    private readonly string _filePath;
    private readonly Dictionary<string, StoredCode> _codes = new(StringComparer.OrdinalIgnoreCase);

    public PasswordResetCodeService(
        IWebHostEnvironment environment,
        ILogger<PasswordResetCodeService> logger)
    {
        _logger = logger;
        _filePath = Path.Combine(environment.ContentRootPath, "App_Data", "password-reset-codes.json");
        LoadFromDisk();
    }

    public void Store(string email, string code, string resetToken)
    {
        var salt = Convert.ToBase64String(RandomNumberGenerator.GetBytes(16));

        lock (_fileLock)
        {
            PurgeExpired();

            _codes[Key(email)] = new StoredCode
            {
                CodeHash = Hash(email, code, salt),
                Salt = salt,
                ResetToken = resetToken,
                ExpiresAt = DateTime.UtcNow.Add(Lifetime)
            };

            SaveToDisk();
        }
    }

    public PasswordResetCodeResult Validate(string email, string code)
    {
        lock (_fileLock)
        {
            PurgeExpired();

            if (!_codes.TryGetValue(Key(email), out var entry) || entry is null)
            {
                return new PasswordResetCodeResult(false, null, "კოდი ვადაგასულია. მოითხოვე ახალი კოდი.");
            }

            if (entry.ExpiresAt < DateTime.UtcNow)
            {
                _codes.Remove(Key(email));
                SaveToDisk();
                return new PasswordResetCodeResult(false, null, "კოდი ვადაგასულია. მოითხოვე ახალი კოდი.");
            }

            if (entry.Attempts >= MaxAttempts)
            {
                _codes.Remove(Key(email));
                SaveToDisk();
                return new PasswordResetCodeResult(false, null, "მცდელობების რაოდენობა ამოიწურა. მოითხოვე ახალი კოდი.");
            }

            entry.Attempts++;
            SaveToDisk();

            var expected = Hash(email, code, entry.Salt);
            if (!CryptographicOperations.FixedTimeEquals(
                    Encoding.UTF8.GetBytes(expected),
                    Encoding.UTF8.GetBytes(entry.CodeHash)))
            {
                return new PasswordResetCodeResult(false, null, "კოდი არასწორია.");
            }

            // Keep the code until the password is actually changed, so a password-policy
            // failure can be corrected without requesting a new code.
            return new PasswordResetCodeResult(true, entry.ResetToken, null);
        }
    }

    public void Remove(string email)
    {
        lock (_fileLock)
        {
            _codes.Remove(Key(email));
            SaveToDisk();
        }
    }

    private void LoadFromDisk()
    {
        try
        {
            if (!File.Exists(_filePath))
            {
                return;
            }

            var json = File.ReadAllText(_filePath);
            var stored = JsonSerializer.Deserialize<Dictionary<string, StoredCode>>(json);

            if (stored is null)
            {
                return;
            }

            foreach (var pair in stored)
            {
                if (pair.Value.ExpiresAt > DateTime.UtcNow)
                {
                    _codes[pair.Key] = pair.Value;
                }
            }
        }
        catch (Exception exception)
        {
            _logger.LogWarning(exception, "Could not load stored password-reset codes.");
        }
    }

    private void SaveToDisk()
    {
        try
        {
            var directory = Path.GetDirectoryName(_filePath);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            File.WriteAllText(
                _filePath,
                JsonSerializer.Serialize(_codes, new JsonSerializerOptions { WriteIndented = true }));
        }
        catch (Exception exception)
        {
            _logger.LogWarning(exception, "Could not persist password-reset codes.");
        }
    }

    private void PurgeExpired()
    {
        var now = DateTime.UtcNow;
        foreach (var key in _codes
                     .Where(pair => pair.Value.ExpiresAt <= now)
                     .Select(pair => pair.Key)
                     .ToList())
        {
            _codes.Remove(key);
        }
    }

    private static string Key(string email) =>
        KeyPrefix + email.Trim().ToLowerInvariant();

    private static string Hash(string email, string code, string salt)
    {
        var value = $"{email.Trim().ToLowerInvariant()}|{code.Trim()}|{salt}";
        return Convert.ToBase64String(SHA256.HashData(Encoding.UTF8.GetBytes(value)));
    }

    public sealed class StoredCode
    {
        public string CodeHash { get; set; } = string.Empty;
        public string Salt { get; set; } = string.Empty;
        public string ResetToken { get; set; } = string.Empty;
        public DateTime ExpiresAt { get; set; }
        public int Attempts { get; set; }
    }
}

using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Caching.Memory;

namespace Obd360.Api.Services;

public sealed record PasswordResetCodeResult(bool Success, string? Token, string? Error);

public interface IPasswordResetCodeService
{
    void Store(string email, string code, string resetToken);

    PasswordResetCodeResult Validate(string email, string code);
}

public sealed class PasswordResetCodeService : IPasswordResetCodeService
{
    private static readonly TimeSpan Lifetime = TimeSpan.FromMinutes(10);
    private const int MaxAttempts = 5;
    private const string KeyPrefix = "password-reset:";

    private readonly IMemoryCache _cache;

    public PasswordResetCodeService(IMemoryCache cache)
    {
        _cache = cache;
    }

    public void Store(string email, string code, string resetToken)
    {
        var salt = Convert.ToBase64String(RandomNumberGenerator.GetBytes(16));

        var entry = new Entry
        {
            CodeHash = Hash(email, code, salt),
            Salt = salt,
            ResetToken = resetToken,
            ExpiresAt = DateTime.UtcNow.Add(Lifetime)
        };

        _cache.Set(Key(email), entry, Lifetime);
    }

    public PasswordResetCodeResult Validate(string email, string code)
    {
        if (!_cache.TryGetValue<Entry>(Key(email), out var entry) || entry is null)
        {
            return new PasswordResetCodeResult(false, null, "კოდი ვადაგასულია. მოითხოვე ახალი კოდი.");
        }

        lock (entry)
        {
            if (entry.ExpiresAt < DateTime.UtcNow)
            {
                _cache.Remove(Key(email));
                return new PasswordResetCodeResult(false, null, "კოდი ვადაგასულია. მოითხოვე ახალი კოდი.");
            }

            if (entry.Attempts >= MaxAttempts)
            {
                _cache.Remove(Key(email));
                return new PasswordResetCodeResult(false, null, "მცდელობების რაოდენობა ამოიწურა. მოითხოვე ახალი კოდი.");
            }

            entry.Attempts++;

            var expected = Hash(email, code, entry.Salt);
            if (!CryptographicOperations.FixedTimeEquals(
                    Encoding.UTF8.GetBytes(expected),
                    Encoding.UTF8.GetBytes(entry.CodeHash)))
            {
                return new PasswordResetCodeResult(false, null, "კოდი არასწორია.");
            }

            _cache.Remove(Key(email));
            return new PasswordResetCodeResult(true, entry.ResetToken, null);
        }
    }

    private static string Key(string email) =>
        KeyPrefix + email.Trim().ToLowerInvariant();

    private static string Hash(string email, string code, string salt)
    {
        var value = $"{email.Trim().ToLowerInvariant()}|{code.Trim()}|{salt}";
        return Convert.ToBase64String(SHA256.HashData(Encoding.UTF8.GetBytes(value)));
    }

    private sealed class Entry
    {
        public string CodeHash { get; init; } = string.Empty;
        public string Salt { get; init; } = string.Empty;
        public string ResetToken { get; init; } = string.Empty;
        public DateTime ExpiresAt { get; init; }
        public int Attempts { get; set; }
    }
}

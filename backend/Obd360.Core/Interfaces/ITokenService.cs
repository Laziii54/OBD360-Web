namespace Obd360.Core.Interfaces;

public record TokenPair(string AccessToken, string RefreshToken, DateTime RefreshExpiresAt);

public interface ITokenService
{
    string CreateAccessToken(Guid userId, string email, IEnumerable<string> roles);
    string CreateRefreshToken();
    string HashRefreshToken(string refreshToken);
}

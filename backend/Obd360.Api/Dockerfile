FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY backend/Obd360.Api/Obd360.Api.csproj backend/Obd360.Api/
COPY backend/Obd360.Core/Obd360.Core.csproj backend/Obd360.Core/
COPY backend/Obd360.Infrastructure/Obd360.Infrastructure.csproj backend/Obd360.Infrastructure/

RUN dotnet restore backend/Obd360.Api/Obd360.Api.csproj

COPY backend/ backend/

RUN dotnet publish backend/Obd360.Api/Obd360.Api.csproj \
    -c Release \
    -o /app/publish \
    --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app

COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080

ENTRYPOINT ["dotnet", "Obd360.Api.dll"]

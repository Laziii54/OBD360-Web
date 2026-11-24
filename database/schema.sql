-- OBD360 Web - SQL Server schema
-- Generated from the development database.
-- Source of truth: EF Core migrations in backend/Obd360.Infrastructure/Migrations.

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE [dbo].[__EFMigrationsHistory] (
    [MigrationId] nvarchar(150) NOT NULL,
    [ProductVersion] nvarchar(32) NOT NULL,
    CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY ([MigrationId])
);
GO

CREATE TABLE [dbo].[Adapters] (
    [Id] uniqueidentifier NOT NULL,
    [UserId] uniqueidentifier NOT NULL,
    [VehicleId] uniqueidentifier NOT NULL,
    [Name] nvarchar(max) NOT NULL,
    [ConnectionType] int NOT NULL,
    [LastConnectedAt] datetime2 NULL,
    CONSTRAINT [PK_Adapters] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AiConversations] (
    [Id] uniqueidentifier NOT NULL,
    [UserId] uniqueidentifier NOT NULL,
    [CreatedAt] datetime2 NOT NULL,
    CONSTRAINT [PK_AiConversations] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AiMessages] (
    [Id] uniqueidentifier NOT NULL,
    [ConversationId] uniqueidentifier NOT NULL,
    [Role] int NOT NULL,
    [Content] nvarchar(max) NOT NULL,
    [CreatedAt] datetime2 NOT NULL,
    CONSTRAINT [PK_AiMessages] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AspNetRoleClaims] (
    [Id] int IDENTITY(1,1) NOT NULL,
    [RoleId] uniqueidentifier NOT NULL,
    [ClaimType] nvarchar(max) NULL,
    [ClaimValue] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetRoleClaims] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AspNetRoles] (
    [Id] uniqueidentifier NOT NULL,
    [Name] nvarchar(256) NULL,
    [NormalizedName] nvarchar(256) NULL,
    [ConcurrencyStamp] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetRoles] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AspNetUserClaims] (
    [Id] int IDENTITY(1,1) NOT NULL,
    [UserId] uniqueidentifier NOT NULL,
    [ClaimType] nvarchar(max) NULL,
    [ClaimValue] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetUserClaims] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AspNetUserLogins] (
    [LoginProvider] nvarchar(450) NOT NULL,
    [ProviderKey] nvarchar(450) NOT NULL,
    [ProviderDisplayName] nvarchar(max) NULL,
    [UserId] uniqueidentifier NOT NULL,
    CONSTRAINT [PK_AspNetUserLogins] PRIMARY KEY ([LoginProvider], [ProviderKey])
);
GO

CREATE TABLE [dbo].[AspNetUserRoles] (
    [UserId] uniqueidentifier NOT NULL,
    [RoleId] uniqueidentifier NOT NULL,
    CONSTRAINT [PK_AspNetUserRoles] PRIMARY KEY ([UserId], [RoleId])
);
GO

CREATE TABLE [dbo].[AspNetUsers] (
    [Id] uniqueidentifier NOT NULL,
    [DisplayName] nvarchar(max) NOT NULL,
    [CreatedAt] datetime2 NOT NULL,
    [UserName] nvarchar(256) NULL,
    [NormalizedUserName] nvarchar(256) NULL,
    [Email] nvarchar(256) NULL,
    [NormalizedEmail] nvarchar(256) NULL,
    [EmailConfirmed] bit NOT NULL,
    [PasswordHash] nvarchar(max) NULL,
    [SecurityStamp] nvarchar(max) NULL,
    [ConcurrencyStamp] nvarchar(max) NULL,
    [PhoneNumber] nvarchar(max) NULL,
    [PhoneNumberConfirmed] bit NOT NULL,
    [TwoFactorEnabled] bit NOT NULL,
    [LockoutEnd] datetimeoffset NULL,
    [LockoutEnabled] bit NOT NULL,
    [AccessFailedCount] int NOT NULL,
    CONSTRAINT [PK_AspNetUsers] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[AspNetUserTokens] (
    [UserId] uniqueidentifier NOT NULL,
    [LoginProvider] nvarchar(450) NOT NULL,
    [Name] nvarchar(450) NOT NULL,
    [Value] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetUserTokens] PRIMARY KEY ([UserId], [LoginProvider], [Name])
);
GO

CREATE TABLE [dbo].[DtcCatalogEntries] (
    [Code] nvarchar(450) NOT NULL,
    [Category] nvarchar(20) NOT NULL,
    [TitleEn] nvarchar(200) NOT NULL,
    [TitleKa] nvarchar(200) NOT NULL,
    [DescriptionEn] nvarchar(max) NOT NULL,
    [DescriptionKa] nvarchar(max) NOT NULL,
    [Difficulty] nvarchar(20) NOT NULL,
    [DiyPossible] bit NOT NULL,
    [EstimatedCostMin] int NULL,
    [EstimatedCostMax] int NULL,
    [EstimatedHoursMin] float NULL,
    [EstimatedHoursMax] float NULL,
    [DetailsJson] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_DtcCatalogEntries] PRIMARY KEY ([Code])
);
GO

CREATE TABLE [dbo].[DtcRecords] (
    [Id] uniqueidentifier NOT NULL,
    [SessionId] uniqueidentifier NOT NULL,
    [Code] nvarchar(max) NOT NULL,
    [Status] int NOT NULL,
    [FreezeFrameJson] nvarchar(max) NULL,
    CONSTRAINT [PK_DtcRecords] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[LiveReadings] (
    [Id] uniqueidentifier NOT NULL,
    [SessionId] uniqueidentifier NOT NULL,
    [CapturedAt] datetime2 NOT NULL,
    [Pid] nvarchar(max) NOT NULL,
    [Value] decimal(10,3) NOT NULL,
    [Unit] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_LiveReadings] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[MaintenanceReminders] (
    [Id] uniqueidentifier NOT NULL,
    [VehicleId] uniqueidentifier NOT NULL,
    [Type] nvarchar(max) NOT NULL,
    [DueAtKm] int NULL,
    [DueAtDate] date NULL,
    [Status] int NOT NULL,
    CONSTRAINT [PK_MaintenanceReminders] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[NotificationLogs] (
    [Id] uniqueidentifier NOT NULL,
    [UserId] uniqueidentifier NOT NULL,
    [Channel] int NOT NULL,
    [Type] int NOT NULL,
    [Status] int NOT NULL,
    [SentAt] datetime2 NOT NULL,
    CONSTRAINT [PK_NotificationLogs] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[RefreshSessions] (
    [Id] uniqueidentifier NOT NULL,
    [UserId] uniqueidentifier NOT NULL,
    [TokenHash] nvarchar(450) NOT NULL,
    [ExpiresAt] datetime2 NOT NULL,
    [RevokedAt] datetime2 NULL,
    CONSTRAINT [PK_RefreshSessions] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[Reports] (
    [Id] uniqueidentifier NOT NULL,
    [VehicleId] uniqueidentifier NOT NULL,
    [Type] int NOT NULL,
    [GeneratedAt] datetime2 NOT NULL,
    [FileUrl] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_Reports] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[ScanSessions] (
    [Id] uniqueidentifier NOT NULL,
    [VehicleId] uniqueidentifier NOT NULL,
    [StartedAt] datetime2 NOT NULL,
    [EndedAt] datetime2 NULL,
    [OdometerKm] int NULL,
    [ConnectionType] int NOT NULL,
    CONSTRAINT [PK_ScanSessions] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [dbo].[UserPreferences] (
    [UserId] uniqueidentifier NOT NULL,
    [UnitSystem] int NOT NULL,
    [Theme] int NOT NULL,
    [NotificationChannel] int NOT NULL,
    CONSTRAINT [PK_UserPreferences] PRIMARY KEY ([UserId])
);
GO

CREATE TABLE [dbo].[Vehicles] (
    [Id] uniqueidentifier NOT NULL,
    [UserId] uniqueidentifier NOT NULL,
    [Vin] nvarchar(max) NULL,
    [Make] nvarchar(max) NOT NULL,
    [Model] nvarchar(max) NOT NULL,
    [Year] int NOT NULL,
    [PlateNumber] nvarchar(max) NULL,
    [CreatedAt] datetime2 NOT NULL,
    CONSTRAINT [PK_Vehicles] PRIMARY KEY ([Id])
);
GO

-- Indexes (kept identical to backend/Obd360.Infrastructure/Migrations)
CREATE INDEX [IX_Adapters_UserId] ON [dbo].[Adapters] ([UserId]);
GO
CREATE UNIQUE INDEX [IX_Adapters_VehicleId] ON [dbo].[Adapters] ([VehicleId]);
GO
CREATE INDEX [IX_AiConversations_UserId] ON [dbo].[AiConversations] ([UserId]);
GO
CREATE INDEX [IX_AiMessages_ConversationId_CreatedAt] ON [dbo].[AiMessages] ([ConversationId], [CreatedAt]);
GO
CREATE INDEX [IX_AspNetRoleClaims_RoleId] ON [dbo].[AspNetRoleClaims] ([RoleId]);
GO
CREATE UNIQUE INDEX [RoleNameIndex] ON [dbo].[AspNetRoles] ([NormalizedName]) WHERE [NormalizedName] IS NOT NULL;
GO
CREATE INDEX [IX_AspNetUserClaims_UserId] ON [dbo].[AspNetUserClaims] ([UserId]);
GO
CREATE INDEX [IX_AspNetUserLogins_UserId] ON [dbo].[AspNetUserLogins] ([UserId]);
GO
CREATE INDEX [IX_AspNetUserRoles_RoleId] ON [dbo].[AspNetUserRoles] ([RoleId]);
GO
CREATE INDEX [EmailIndex] ON [dbo].[AspNetUsers] ([NormalizedEmail]);
GO
CREATE UNIQUE INDEX [UserNameIndex] ON [dbo].[AspNetUsers] ([NormalizedUserName]) WHERE [NormalizedUserName] IS NOT NULL;
GO
CREATE INDEX [IX_DtcCatalogEntries_Category] ON [dbo].[DtcCatalogEntries] ([Category]);
GO
CREATE INDEX [IX_DtcRecords_SessionId] ON [dbo].[DtcRecords] ([SessionId]);
GO
CREATE INDEX [IX_LiveReadings_SessionId_CapturedAt] ON [dbo].[LiveReadings] ([SessionId], [CapturedAt]);
GO
CREATE INDEX [IX_MaintenanceReminders_VehicleId_Status] ON [dbo].[MaintenanceReminders] ([VehicleId], [Status]);
GO
CREATE INDEX [IX_NotificationLogs_UserId_SentAt] ON [dbo].[NotificationLogs] ([UserId], [SentAt]);
GO
CREATE UNIQUE INDEX [IX_RefreshSessions_TokenHash] ON [dbo].[RefreshSessions] ([TokenHash]);
GO
CREATE INDEX [IX_RefreshSessions_UserId] ON [dbo].[RefreshSessions] ([UserId]);
GO
CREATE INDEX [IX_Reports_VehicleId] ON [dbo].[Reports] ([VehicleId]);
GO
CREATE INDEX [IX_ScanSessions_VehicleId_StartedAt] ON [dbo].[ScanSessions] ([VehicleId], [StartedAt]);
GO
CREATE INDEX [IX_Vehicles_UserId] ON [dbo].[Vehicles] ([UserId]);
GO

-- Foreign keys
ALTER TABLE [dbo].[Adapters] ADD CONSTRAINT [FK_Adapters_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[Adapters] ADD CONSTRAINT [FK_Adapters_Vehicles_VehicleId] FOREIGN KEY ([VehicleId]) REFERENCES [dbo].[Vehicles] ([Id]);
GO
ALTER TABLE [dbo].[AiConversations] ADD CONSTRAINT [FK_AiConversations_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[AiMessages] ADD CONSTRAINT [FK_AiMessages_AiConversations_ConversationId] FOREIGN KEY ([ConversationId]) REFERENCES [dbo].[AiConversations] ([Id]);
GO
ALTER TABLE [dbo].[AspNetRoleClaims] ADD CONSTRAINT [FK_AspNetRoleClaims_AspNetRoles_RoleId] FOREIGN KEY ([RoleId]) REFERENCES [dbo].[AspNetRoles] ([Id]);
GO
ALTER TABLE [dbo].[AspNetUserClaims] ADD CONSTRAINT [FK_AspNetUserClaims_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[AspNetUserLogins] ADD CONSTRAINT [FK_AspNetUserLogins_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[AspNetUserRoles] ADD CONSTRAINT [FK_AspNetUserRoles_AspNetRoles_RoleId] FOREIGN KEY ([RoleId]) REFERENCES [dbo].[AspNetRoles] ([Id]);
GO
ALTER TABLE [dbo].[AspNetUserRoles] ADD CONSTRAINT [FK_AspNetUserRoles_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[AspNetUserTokens] ADD CONSTRAINT [FK_AspNetUserTokens_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[DtcRecords] ADD CONSTRAINT [FK_DtcRecords_ScanSessions_SessionId] FOREIGN KEY ([SessionId]) REFERENCES [dbo].[ScanSessions] ([Id]);
GO
ALTER TABLE [dbo].[LiveReadings] ADD CONSTRAINT [FK_LiveReadings_ScanSessions_SessionId] FOREIGN KEY ([SessionId]) REFERENCES [dbo].[ScanSessions] ([Id]);
GO
ALTER TABLE [dbo].[MaintenanceReminders] ADD CONSTRAINT [FK_MaintenanceReminders_Vehicles_VehicleId] FOREIGN KEY ([VehicleId]) REFERENCES [dbo].[Vehicles] ([Id]);
GO
ALTER TABLE [dbo].[NotificationLogs] ADD CONSTRAINT [FK_NotificationLogs_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[RefreshSessions] ADD CONSTRAINT [FK_RefreshSessions_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[Reports] ADD CONSTRAINT [FK_Reports_Vehicles_VehicleId] FOREIGN KEY ([VehicleId]) REFERENCES [dbo].[Vehicles] ([Id]);
GO
ALTER TABLE [dbo].[ScanSessions] ADD CONSTRAINT [FK_ScanSessions_Vehicles_VehicleId] FOREIGN KEY ([VehicleId]) REFERENCES [dbo].[Vehicles] ([Id]);
GO
ALTER TABLE [dbo].[UserPreferences] ADD CONSTRAINT [FK_UserPreferences_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO
ALTER TABLE [dbo].[Vehicles] ADD CONSTRAINT [FK_Vehicles_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [dbo].[AspNetUsers] ([Id]);
GO

-- End of schema

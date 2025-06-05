# Microsoft Teams Integration for Outlook MCP Server

This document describes the Teams functionality that has been added to your existing Outlook MCP server.

## Overview

The Teams integration adds 4 essential tools for Microsoft Teams channel messaging functionality:

1. `teams-list-teams` - List all teams the user has access to
2. `teams-list-channels` - List channels in a specific team  
3. `teams-send-channel-message` - Send a message to a team channel
4. `teams-read-channel-messages` - Read recent messages from a channel

## Configuration Updates

### Environment Variables

No new environment variables are required. The integration uses your existing Azure app registration and Microsoft Graph API setup.

### Updated Permissions

The following Microsoft Graph API permissions have been added to your application scopes:

- `Team.ReadBasic.All` - Read basic team information
- `Channel.ReadBasic.All` - Read basic channel information
- `ChannelMessage.Read.All` - Read channel messages
- `ChannelMessage.Send` - Send messages to channels

### Azure App Registration

You'll need to update your Azure app registration to include these new permissions:

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Select your existing Outlook MCP app
3. Go to "API permissions"
4. Click "Add a permission" → Microsoft Graph → Delegated permissions
5. Add these permissions:
   - Microsoft Graph → Team.ReadBasic.All
   - Microsoft Graph → Channel.ReadBasic.All  
   - Microsoft Graph → ChannelMessage.Read.All
   - Microsoft Graph → ChannelMessage.Send
6. Click "Grant admin consent" for your organization

## Available Tools

### 1. teams-list-teams

Lists all Microsoft Teams that the user has access to.

**Parameters:**
- `count` (optional): Number of teams to retrieve (default: 25, max: 50)

**Example:**
```json
{
  "name": "teams-list-teams",
  "arguments": {
    "count": 10
  }
}
```

### 2. teams-list-channels

Lists channels in a specific Microsoft Team.

**Parameters:**
- `teamId` (required): ID of the team to list channels for
- `channelType` (optional): Filter by channel type ("standard", "private", "shared")

**Example:**
```json
{
  "name": "teams-list-channels", 
  "arguments": {
    "teamId": "19:abc123def456...",
    "channelType": "standard"
  }
}
```

### 3. teams-send-channel-message

Sends a message to a Microsoft Teams channel.

**Parameters:**
- `teamId` (required): ID of the team containing the channel
- `channelId` (required): ID of the channel to send message to
- `message` (required): Message content to send
- `contentType` (optional): Content type ("text" or "html", default: "text")

**Example:**
```json
{
  "name": "teams-send-channel-message",
  "arguments": {
    "teamId": "19:abc123def456...",
    "channelId": "19:def456ghi789...",
    "message": "Hello from the MCP server!",
    "contentType": "text"
  }
}
```

### 4. teams-read-channel-messages

Reads recent messages from a Microsoft Teams channel.

**Parameters:**
- `teamId` (required): ID of the team containing the channel
- `channelId` (required): ID of the channel to read messages from
- `count` (optional): Number of messages to retrieve (default: 20, max: 50)

**Example:**
```json
{
  "name": "teams-read-channel-messages",
  "arguments": {
    "teamId": "19:abc123def456...",
    "channelId": "19:def456ghi789...",
    "count": 10
  }
}
```

## Testing Instructions

### Prerequisites
1. Ensure your existing Outlook MCP server is working
2. Update Azure app permissions as described above
3. Re-authenticate to get tokens with new permissions

### Basic Testing Workflow

1. **List your teams:**
   ```bash
   # Use Claude or your MCP client to call:
   teams-list-teams
   ```

2. **List channels in a team:**
   ```bash
   # Copy a team ID from step 1, then call:
   teams-list-channels with teamId: "your-team-id-here"
   ```

3. **Read messages from a channel:**
   ```bash
   # Copy team and channel IDs from previous steps, then call:
   teams-read-channel-messages with teamId and channelId
   ```

4. **Send a test message:**
   ```bash
   # Send a test message to verify write permissions:
   teams-send-channel-message with teamId, channelId, and message: "Test from MCP"
   ```

### Expected Responses

All tools return JSON responses with this structure:

**Success Response:**
```json
{
  "success": true,
  "data": "...",
  // Additional response-specific fields
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description",
  // Additional context fields
}
```

### Common Issues and Solutions

**403 Forbidden Errors:**
- Check that you've added the required permissions to your Azure app
- Ensure admin consent has been granted
- Re-authenticate to refresh your token with new permissions

**404 Not Found Errors:**
- Verify team and channel IDs are correct
- Ensure you have access to the specified team/channel
- Team/channel may have been deleted or archived

**Authentication Errors:**
- Your existing auth flow should work unchanged
- If auth fails, restart the auth process: `outlook-auth-login`

## File Structure

The Teams integration follows your existing modular structure:

```
outlook-mcp/
├── teams/
│   ├── index.js                    # Main Teams module export
│   ├── list-teams.js              # List teams handler
│   ├── list-channels.js           # List channels handler  
│   ├── send-channel-message.js    # Send message handler
│   └── read-channel-messages.js   # Read messages handler
├── index.js                       # Updated to include Teams tools
├── config.js                      # Updated with Teams permissions
└── TEAMS_INTEGRATION.md           # This documentation
```

## Limitations (MVP Scope)

This is a minimal viable implementation with these intentional limitations:

- **Channel messaging only** - No direct/private messages
- **No real-time notifications** - Only on-demand API calls
- **No message editing/deletion** - Send and read only
- **No file attachments** - Text messages only
- **No advanced Teams features** - No apps, tabs, meetings, etc.

## Future Enhancements

Potential additions for future versions:
- Direct message support
- File attachment handling
- Message reactions and mentions
- Meeting integration
- Real-time webhook notifications
- Advanced message formatting
- Teams app integration

## Error Handling

The integration includes comprehensive error handling:
- Microsoft Graph API error translation
- Permission-specific error messages
- Input validation with helpful feedback
- Consistent error response format
- Proper logging for debugging

All errors are logged to stderr for debugging while returning user-friendly error messages to the MCP client. 
/**
 * Configuration for Outlook MCP Server
 */
const path = require('path');
const os = require('os');

// Ensure we have a home directory path even if process.env.HOME is undefined
const homeDir = process.env.HOME || process.env.USERPROFILE || os.homedir() || '/tmp';

module.exports = {
  // Server information
  SERVER_NAME: "outlook-assistant",
  SERVER_VERSION: "1.0.0",
  
  // Test mode setting
  USE_TEST_MODE: process.env.USE_TEST_MODE === 'true',
  
  // Authentication configuration
  AUTH_CONFIG: {
    clientId: process.env.MS_CLIENT_ID || '',
    clientSecret: process.env.MS_CLIENT_SECRET || '',
    redirectUri: 'http://localhost:3333/auth/callback',
    scopes: [
      // Email permissions
      'Mail.Read', 
      'Mail.ReadWrite', 
      'Mail.Send', 
      // User permissions
      'User.Read', 
      // Calendar permissions
      'Calendars.Read', 
      'Calendars.ReadWrite',
      // Teams permissions for MVP
      'Team.ReadBasic.All',
      'Channel.ReadBasic.All', 
      'ChannelMessage.Read.All',
      'ChannelMessage.Send'
    ],
    tokenStorePath: path.join(homeDir, '.outlook-mcp-tokens.json'),
    authServerUrl: 'http://localhost:3333'
  },
  
  // Microsoft Graph API
  GRAPH_API_ENDPOINT: 'https://graph.microsoft.com/v1.0/',
  
  // Calendar constants
  CALENDAR_SELECT_FIELDS: 'id,subject,start,end,location,bodyPreview,isAllDay,recurrence,attendees',

  // Email constants
  EMAIL_SELECT_FIELDS: 'id,subject,from,toRecipients,ccRecipients,receivedDateTime,bodyPreview,hasAttachments,importance,isRead',
  EMAIL_DETAIL_FIELDS: 'id,subject,from,toRecipients,ccRecipients,bccRecipients,receivedDateTime,bodyPreview,body,hasAttachments,importance,isRead,internetMessageHeaders',
  
  // Calendar constants
  CALENDAR_SELECT_FIELDS: 'id,subject,bodyPreview,start,end,location,organizer,attendees,isAllDay,isCancelled',
  
  // Teams constants
  TEAMS_SELECT_FIELDS: 'id,displayName,description,webUrl,isArchived,visibility,createdDateTime,memberSettings',
  CHANNELS_SELECT_FIELDS: 'id,displayName,description,webUrl,membershipType,createdDateTime,isFavoriteByDefault,email',
  MESSAGES_SELECT_FIELDS: 'id,createdDateTime,lastModifiedDateTime,messageType,importance,webUrl,from,body,mentions,reactions',
  
  // Pagination
  DEFAULT_PAGE_SIZE: 25,
  MAX_RESULT_COUNT: 50
};

/**
 * List Channels handler
 */
const { callGraphAPI } = require('../utils/graph-api');
const { ensureAuthenticated } = require('../auth');

async function handleListChannels(args) {
  try {
    const { teamId, channelType } = args;
    
    // Validate required parameters
    if (!teamId) {
      throw new Error('teamId is required');
    }

    // Get access token
    const accessToken = await ensureAuthenticated();
    
    // Build query parameters
    const queryParams = {};
    if (channelType) {
      queryParams.$filter = `membershipType eq '${channelType}'`;
    }
    
    // Get team channels
    const response = await callGraphAPI(accessToken, 'GET', `teams/${teamId}/channels`, null, queryParams);

    const channels = response.value.map(channel => ({
      id: channel.id,
      displayName: channel.displayName,
      description: channel.description || '',
      webUrl: channel.webUrl,
      membershipType: channel.membershipType,
      createdDateTime: channel.createdDateTime,
      isFavoriteByDefault: channel.isFavoriteByDefault || false,
      email: channel.email || ''
    }));

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            teamId: teamId,
            count: channels.length,
            channels: channels
          }, null, 2)
        }
      ]
    };

  } catch (error) {
    console.error('Error listing channels:', error);
    
    if (error.message === 'Authentication required') {
      return {
        content: [{ 
          type: "text", 
          text: "Authentication required. Please use the 'authenticate' tool first."
        }]
      };
    }
    
    let errorMessage = 'Failed to list channels';
    if (error.message.includes('403')) {
      errorMessage = 'Insufficient permissions to list channels. Please ensure the application has Channel.ReadBasic.All permission.';
    } else if (error.message.includes('401')) {
      errorMessage = 'Authentication failed. Please ensure you are logged in.';
    } else if (error.message.includes('404')) {
      errorMessage = `Team with ID '${args.teamId}' not found or you don't have access to it.`;
    } else if (error.message) {
      errorMessage = error.message;
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: false,
            error: errorMessage,
            teamId: args.teamId
          }, null, 2)
        }
      ]
    };
  }
}

module.exports = handleListChannels; 
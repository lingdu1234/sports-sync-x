# Sports Sync X

A tool for automatically syncing workout records between Garmin.cn, Garmin.com, and Coros platforms. It supports automatic detection and deletion of duplicate records, with enterprise WeChat notification support.

## Features

- **Multi-platform Sync**: Supports Garmin CN, Garmin COM, and Coros fitness platforms
- **Duplicate Detection**: Automatically detects duplicate workout records with configurable auto-deletion
- **Smart Sync**: Intelligently determines whether sync is needed based on workout time and other information
- **FIT File Processing**: Supports downloading and uploading FIT format workout data files
- **Database Storage**: Uses SQLite database for storing workout records for easy management and querying
- **Message Notifications**: Supports enterprise WeChat bot notifications for sync completion status
- **Flexible Configuration**: Configure sync platforms and account information via environment variables

## Requirements

- Python >= 3.14
- uv (package manager)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd sports-sync-x
```

2. Install dependencies using uv:

```bash
uv sync
```

## Configuration

1. Copy the environment variable configuration file:

```bash
cp .env.example .env
```

2. Edit the `.env` file and fill in the relevant configuration:

```env
# Platforms to sync (separate multiple platforms with commas)
SYNC_PLATFORM=GARMINCN,GARMINCOM,COROS

# Garmin COM account configuration
GARMIN_EMAIL_COM=your_garmin_email@example.com
GARMIN_PASSWORD_COM=your_garmin_password

# Garmin CN account configuration
GARMIN_EMAIL_CN=your_garmin_email@example.com
GARMIN_PASSWORD_CN=your_garmin_password

# Coros account configuration
COROS_EMAIL=your_coros_email@example.com
COROS_PASSWORD=your_coros_password

# Number of latest records to fetch from Garmin
GARMIN_NEWEST_NUM=10000

# Whether to automatically delete duplicate records (1=delete, 0=don't delete)
DELETE_DUPLICATE=1

# Workout time difference threshold (seconds), used to determine if records are duplicates
SPORT_DIFF_SECOND=60

# Enterprise WeChat bot Key (optional)
QYWX_BOT_KEY=your_qywx_bot_key
```

## Usage

Run the sync program:

```bash
uv run x-sync.py
```

Or run directly with Python:

```bash
python x-sync.py
```

## Workflow

The program performs the following steps:

1. **Initialize Database**: Create SQLite database for storing workout records
2. **Fetch Workout Records**: Fetch all workout records from configured platforms
3. **Process Duplicate Records**:
   - Sort workout records by activity_id
   - Save to database and detect duplicate records
   - If `DELETE_DUPLICATE=1` is configured, automatically delete duplicate records
4. **Check Sync Status**: Check sync status of each workout record across platforms
5. **Sync Workout Records**:
   - Download FIT files of unsynced workout records
   - Upload to target platforms
   - Update sync status
6. **Send Notification**: Send sync completion notification via enterprise WeChat bot

## Project Structure

```tree
sports-sync-x/
├── app/
│   ├── coros/           # Coros platform related code
│   ├── database/         # Database operations
│   ├── garmin/          # Garmin platform related code
│   ├── oss/             # OSS clients (Alibaba Cloud/AWS)
│   ├── sync_fn/         # Sync functionality implementation
│   └── utils/           # Utility functions
├── tests/               # Test files
├── x-sync.py            # Program entry point
├── pyproject.toml       # Project configuration
├── .env.example         # Environment variable example
└── README.md            # Project documentation
```

## Supported Sport Types

The program supports various sport types, including but not limited to:

- Running (treadmill, trail running, virtual running, etc.)
- Cycling (road cycling, indoor cycling, gravel cycling, etc.)
- Swimming (pool swimming, open water swimming, etc.)
- Fitness (strength training, indoor cardio, HIIT, etc.)
- Outdoor activities (hiking, mountaineering, rock climbing, etc.)
- Ball sports (basketball, soccer, tennis, etc.)
- Water sports (kayaking, surfing, sailing, etc.)

For complete sport type mapping, please refer to [app/utils/const.py](app/utils/const.py)

## Data Storage

- **Database File**: `db/sports_sync.sqlite`
- **FIT File Storage**:
  - Garmin COM: `fit/garmin_com/`
  - Garmin CN: `fit/garmin_cn/`
  - Coros: `fit/coros/`

## Important Notes

1. **Account Security**: Please keep the account and password information in the `.env` file secure. Do not commit it to version control
2. **API Limits**: Each platform's API may have rate limits. Please set sync intervals reasonably
3. **Network Environment**: Garmin CN requires access within mainland China network environment
4. **Duplicate Records**: Deleting duplicate records is irreversible. Please configure the `DELETE_DUPLICATE` option carefully
5. **Data Backup**: It is recommended to regularly backup the database file and FIT files

## Troubleshooting

### Authentication Failure

- Check if the account and password in the `.env` file are correct
- Confirm if the account has enabled two-factor authentication (if required, disable it or use app-specific passwords)

### Sync Failure

- Check if the network connection is working properly
- Confirm if the target platform's API is functioning normally
- Check the error information output in the console

### Duplicate Records Not Deleted (Please note deletion risks and backup data in time)

- Confirm that `DELETE_DUPLICATE=1` is configured correctly
- Check if the `SPORT_DIFF_SECOND` threshold setting is reasonable

## Acknowledgments

This project references and uses code from the following open-source projects:

- **[garmin-sync-coros](https://github.com/XiaoSiHwang/garmin-sync-coros)** - Thanks to @XiaoSiHwang for providing Garmin and Coros platform sync code
- **[running_page](https://github.com/yihong0618/running_page)** - Thanks to @yihong0618 for their selfless contribution. The Garmin module code in this project references this project

We also thank the following open-source libraries for their support:

- **[garth](https://github.com/matin/garth)** - Garmin Connect API client
- **[SQLModel](https://github.com/tiangolo/sqlmodel)** - Python SQL ORM
- **[fitdecode](https://github.com/polyvertex/fitdecode)** - FIT file decoder library
- **[boto3](https://github.com/boto/boto3)** - AWS SDK for Python
- **[oss2](https://github.com/aliyun/aliyun-oss-python-sdk)** - Alibaba Cloud OSS SDK for Python
- **[requests](https://github.com/psf/requests)** - Python HTTP library
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Read environment variables from .env file

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

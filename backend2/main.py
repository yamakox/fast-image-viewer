import uvicorn
import env


def main():
    uvicorn.run(
        'app.main:app',
        host=env.HOST,
        port=env.PORT,
        log_level='info',
        reload=env.DEBUG,
        workers=1 if env.DEBUG else env.WORKERS,
    )


if __name__ == '__main__':
    main()

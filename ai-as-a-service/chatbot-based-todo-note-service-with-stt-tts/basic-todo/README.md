# Basic ToDo Service

Before deploying the service, you need to set up environment variables that are defined in the `default-environment.ev` file.
First, modify the values of the variables in that file with suitable values.
Then, set the environment variables by running the following command:

```bash
$ source default-environment.ev
```

## CI/CD

### Pre-requisites

- Check environment variables are set properly

```sh
$ ./check-env.sh
```

### Deploy

- Deploy the services

```sh
$ ./deploy.sh
```

### [Optional] Remove the service if required

```sh
$ ./remove.sh
```

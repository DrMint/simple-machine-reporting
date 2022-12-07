# Simple Machine Reporting

A program to send mails to report when certain threshold are met (such as disk usage)

1. Install the requirements using:

   ```bash
   pip3 install -r requirements.txt
   ```

2. Copy .env.example as .env and modify it to your needs:

   ```bash
   cp .env.example .env
   nano .env
   ```

3. Run the script once to check if everything is working:

   ```sh
   python3 /absolute/path/to/simple-machine-reporting/check.py
   ```

4. If it works, create a cron job that runs every X minutes. Here we'll choose every 5 minutes:

   1. First run:

      ```sh
      crontab -e
      ```

   2. Add the following line at the end (make sure to change the absolute path)
      ```cron
      */5 *  *   *   *     python3 /absolute/path/to/simple-machine-reporting/check.py
      ```

To test if the program is working, you can try creating a fake file with a specific size that would trigger the warning (but avoid actually maxing out your disk). Here's an example for creating a (fake) 10GB file

```
fallocate -l 10G gentoo_root.img
```

You can then remove it after receiving the mail as expected.

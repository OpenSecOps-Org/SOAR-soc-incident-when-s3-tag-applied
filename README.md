# soc-incident-when-tag-applied

Whenever certain tags are applied to an S3 bucket, this SAM project
creates incidents for SOC to investigate. The implementation is based
on all member accounts passing the PutBucketTagging event to the custom
event bus `SOAR-events` in the organisation account.

This SAM project is deployed in the organisation account, in each
supported region.

To make the accounts forward this event, it also deploys 
`cloudformation/detect-bucket-tagging.yaml`
to the org account in each supported region, then as a StackSet to all
accounts and all supported regions.


## Deployment

First make sure that your SSO setup is configured with a default profile giving you AWSAdministratorAccess
to your AWS Organizations administrative account. This is necessary as the AWS cross-account role used 
during deployment only can be assumed from that account.

```console
aws sso login
```

Then type:

```console
./deploy
```

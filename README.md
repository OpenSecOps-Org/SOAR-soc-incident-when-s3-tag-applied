# soc-incident-when-tag-applied

Whenever certain tags are applied to an S3 bucket, this SAM project
creates incidents for SOC to investigate. The implementation is based
on all member accounts passing the PutBucketTagging event to the custom
event bus `security-hub-automation` in the organisation account.

This SAM project is deployed in the organisation account, in each
supported region.

To make the accounts forward this event, it also deploys 
`cloudformation/detect-bucket-tagging.yaml`
to the org account in each supported region, then as a StackSet to all
accounts and all supported regions.


## Deployment

First log in to your AWS organisation using SSO and a profile that gives yous
AWSAdministratorAccess to the AWS Organizations admin account.

```console
aws sso login --profile <profile-name>
```

Then type:

```console
./deploy
```

<!--
  教师端-创建上课记录：下拉选择已分配的学生
-->
<template>
  <div class="page-container">
    <h3>创建上课记录</h3>
    <el-card style="max-width:600px;margin-top:16px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" size="large">
        <el-form-item label="选择学生" prop="student_id">
          <el-select v-model="form.student_id" filterable placeholder="选择学生" style="width:100%">
            <el-option
              v-for="s in studentList"
              :key="s.student_id"
              :label="`${s.student_name} (${s.student_grade})`"
              :value="s.student_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型" prop="course_type_id">
          <el-select v-model="form.course_type_id" placeholder="选择课程类型" style="width:100%">
            <el-option v-for="c in courseTypes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课时间" prop="date">
          <el-date-picker
            v-model="form.date" type="datetime" placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="课时数" prop="hours">
          <el-input-number v-model="form.hours" :min="0.5" :step="0.5" :precision="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="上课内容">
          <el-input v-model="form.content" type="textarea" :rows="3" placeholder="本次上课内容摘要..." />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit('pending')">提交审核</el-button>
          <el-button :loading="savingDraft" @click="handleSubmit('draft')">保存草稿</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { teacherApi } from '@/api/teacher'

const formRef = ref<FormInstance>()
const submitting = ref(false)
const savingDraft = ref(false)
const studentList = ref<any[]>([])
const courseTypes = ref<any[]>([])

const form = reactive({
  student_id: null as number | null,
  course_type_id: null as number | null,
  date: '',
  hours: 2,
  content: '',
})

// 禁用未来日期
function disabledDate(time: Date) {
  return time.getTime() > Date.now()
}

const rules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_type_id: [{ required: true, message: '请选择课程类型', trigger: 'change' }],
  date: [
    { required: true, message: '请选择日期时间', trigger: 'change' },
    { validator: (_rule, value, cb) => {
      if (value && new Date(value).getTime() > Date.now()) {
        cb(new Error('上课时间不能是未来时间'))
      } else { cb() }
    }, trigger: 'change' },
  ],
  hours: [{ required: true, message: '请输入课时数', trigger: 'blur' }],
}

onMounted(async () => {
  const [sRes, ctRes] = await Promise.all([
    teacherApi.getMyStudents(),
    teacherApi.getCourseTypes(),
  ])
  studentList.value = sRes.data.data
  courseTypes.value = ctRes.data.data.filter((c: any) => c.is_active)
})

function resetForm() {
  form.student_id = null
  form.course_type_id = null
  form.date = ''
  form.hours = 2
  form.content = ''
}

async function handleSubmit(status: string) {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (status === 'draft') savingDraft.value = true
  else submitting.value = true
  try {
    await teacherApi.createRecord({
      student_id: form.student_id,
      course_type_id: form.course_type_id,
      date: form.date,
      hours: form.hours,
      content: form.content,
      status,
    })
    ElMessage.success(status === 'draft' ? '草稿已保存' : '上课记录已提交，等待管理员审核')
    resetForm()
  } finally {
    submitting.value = false
    savingDraft.value = false
  }
}
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
</style>
